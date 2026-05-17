# Arquitectura Agentil de Generación de Código para IoT (Edge AI)

Esta arquitectura fue diseñada específicamente para operar en dispositivos con recursos limitados (como una Raspberry Pi 5 de 8GB), optimizando el uso de memoria RAM, controlando la temperatura (evitando Thermal Throttling) y maximizando la precisión del modelo pequeño (Qwen2.5-Coder de 3B/1.5B).

## Diagrama de Arquitectura (Con Enrutador Inteligente)

```mermaid
flowchart TD
    User([Usuario / CLI]) -->|Input| Router{Enrutador de Intención\n(Capa Inteligente)}
    
    %% Ruta Conversacional
    Router -->|"QUESTION" (Pregunta)"| Memoria[Capa 2: Memoria RAG ChromaDB]
    Memoria -->|Recupera Contexto| SLM_Chat[Capa 4: Generación Conversacional]
    SLM_Chat -->|Texto Natural| User
    
    %% Ruta de Código
    Router -->|"CODE" (Generar Código)| Planner[Capa 3: Planificador]
    Planner -->|Divide en Subtareas| Loop[Ejecución Secuencial Edge]
    
    subgraph Bucle de Generación y Validación (Por Subtarea)
        Loop --> RAG_Code[Capa 2: RAG]
        RAG_Code -->|Contexto Previo| SLM_Code[Capa 4: Inferencia LLM]
        SLM_Code -->|Extrae solo Python| Validator{Capa 5: Validador Ruff}
        
        Validator -->|Error Sintaxis| Rollback[Rollback Activado\n(Máx 3 intentos)]
        Rollback --> SLM_Code
    end
    
    Validator -->|Sintaxis Correcta 100/100| Ensamblaje[Ensamblador Global]
    Ensamblaje -->|Código Completo| File[Guarda en resultado_final.py]
    Ensamblaje -->|Aprende| Memoria
```

---

## Las 5 Capas en Detalle (Implementación Real)

### Capa 1 — Orquestador Central (Python puro, Asyncio)
Es el "cerebro" y director de orquesta. Mantiene el estado global, mide los tiempos de ejecución y coordina el paso de información entre las demás capas. 
**Mejora Integrada:** Incluye un **Patrón de Enrutador (Router Agent)** que clasifica la intención del usuario. Si es una pregunta, salta la validación de código para no romper el sistema y permite chatear con el modelo de forma natural.

### Capa 2 — Gestión de Contexto y Memoria (RAG + ChromaDB)
La memoria a largo plazo del sistema. 
- Utiliza la base de datos vectorial `ChromaDB` con el modelo de embeddings `all-MiniLM-L6-v2` (se descarga localmente la primera vez que se ejecuta, pesando ~80MB). 
- Cada vez que la Capa 5 aprueba un código exitoso, esta capa lo convierte en vectores matemáticos y lo guarda. Cuando el usuario pide una extensión del código en el futuro, inyecta este contexto en el prompt para que el modelo "recuerde" las variables y clases previas.

### Capa 3 — Planificador (Descomposición)
Se encarga de trocear la tarea general. Para escenarios conversacionales dinámicos o tareas concretas, pasa la solicitud directa. En proyectos grandes, descompone la meta en subtareas con un **grafo de dependencias**.
- **Decisión Arquitectónica Clave:** Las subtareas **NO se ejecutan en paralelo**. Esto es mandatorio para Raspberry Pi, ya que lanzar múltiples inferencias de LLMs en paralelo causaría un colapso por falta de memoria (OOM) o sobrecalentamiento crítico de la CPU (Thermal Throttling).

### Capa 4 — Generación (SLM Local con Ollama)
El motor de inteligencia, ejecutando `qwen2.5-coder:3b`.
- Se configuró con `temperature: 0.1` para que el código sea determinista y preciso.
- **Sin Límite de Tokens:** Se estableció `num_predict: -1` para desactivar el corte prematuro. Esto permite que el modelo escriba algoritmos gigantescos (como un Árbol Rojo-Negro completo) usando todo su Context Window sin que el código quede incompleto.
- Extrae inteligentemente el código puro ignorando el formato "Markdown" de la respuesta del LLM.

### Capa 5 — Validación Estricta + Rollback Adaptativo
El control de calidad autónomo.
- Usa `ruff` (`--select=E9,F63,F7,F82`) para verificar si el código generado es ejecutable en Python. Se configuró para detectar únicamente **errores fatales de sintaxis** (variables no definidas, mala indentación), ignorando alertas cosméticas (linting menor) que podrían rechazar código funcional.
- Si el código falla, el **Mecanismo de Rollback** descarta la basura generada, imprime el motivo exacto del rechazo en consola y obliga a la Capa 4 a intentar generarlo de nuevo, protegiendo así el archivo final de errores que romperían el servidor en producción.
