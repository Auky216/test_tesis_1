import asyncio
import time
from models import GlobalState
from context_manager import ContextManager
from planner import Planner
from generator import CodeGenerator
from validator import Validator

class Orchestrator:
    """
    Capa 1: Orquestador Central.
    """
    def __init__(self):
        self.context_manager = ContextManager()
        self.planner = Planner()
        self.generator = CodeGenerator()
        self.validator = Validator()
        self.state = GlobalState(task_description="")
        
    async def execute_task(self, task: str):
        print(f"\n[ORQUESTADOR] Analizando intención de la petición...")
        intent = await self.generator.classify_intent(task)
        
        if intent == "QUESTION":
            print(f"[ENRUTADOR] Intención detectada: CONVERSACIÓN/PREGUNTA.")
            context = self.context_manager.retrieve_context(task)
            answer = await self.generator.answer_question(task, context)
            print("\n[🤖 RESPUESTA DEL ASISTENTE]:")
            print("="*50)
            print(answer)
            print("="*50)
            return

        print(f"[ENRUTADOR] Intención detectada: GENERAR CÓDIGO.")
        print(f"[ORQUESTADOR] Procesando petición: '{task}'")
        self.state.task_description = task
        
        # --- Capa 3: Planificación ---
        self.state.subtasks = await self.planner.decompose_task(task)
        
        for subtask in self.state.subtasks:
            
            # --- Capa 2: Contexto RAG ---
            context = self.context_manager.retrieve_context(subtask.description)
            error_feedback = ""
            
            while subtask.status != "validated" and subtask.attempts < 3:
                subtask.attempts += 1
                print(f"\n[*] Solicitando código a Qwen2.5-Coder (Intento {subtask.attempts}/3)...")
                
                # Inyectar error previo si existe (Self-Reflection)
                prompt_context = context
                if error_feedback:
                    prompt_context += f"\n\n# IMPORTANTE - CORRIGE ESTE ERROR DEL INTENTO ANTERIOR:\n{error_feedback}"
                
                # --- Capa 4: Generación ---
                code = await self.generator.generate_code(subtask.description, prompt_context)
                subtask.code = code
                
                # --- Capa 5: Validación ---
                is_valid, metrics = self.validator.validate_all(code)
                
                if is_valid:
                    subtask.status = "validated"
                    error_feedback = ""
                    print(f"[VALIDADOR] Éxito. Código ejecutable (Score: {metrics.get('score')}/100)")
                    print(f"\n[DEBUG] --- CÓDIGO ACEPTADO ---\n{code}\n" + "-"*30)
                else:
                    error_type = metrics.get('error_type')
                    details = metrics.get('details', 'Sin detalles')
                    error_feedback = details
                    print(f"[VALIDADOR] Fallo ({error_type}). Rollback activado.")
                    print(f"[MOTIVO DEL RECHAZO]:\n{details}")
                    print(f"\n[DEBUG] --- CÓDIGO FALLIDO ---\n{code}\n" + "-"*30)
                    
        final_code = ""
        for subtask in self.state.subtasks:
            if subtask.status == "validated" and subtask.code:
                final_code += subtask.code + "\n"
        
        if final_code.strip():
            # Guardar el conocimiento en ChromaDB (Memoria)
            self.context_manager.add_to_context(task, final_code)
            
            with open("resultado_final.py", "w") as f:
                f.write(final_code)
            print("[*] Código final ensamblado y guardado en 'resultado_final.py'\n")
        else:
            print("[!] No se pudo generar un código válido después de los intentos.")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    print("\n" + "="*60)
    print("🤖 CHAT AGENTIL INICIADO (Escribe 'salir' para terminar)")
    print("============================================================")
    
    while True:
        try:
            task = input("\n[TU]: ")
            if task.lower() in ['salir', 'exit', 'quit']:
                print("¡Hasta luego!")
                break
            if not task.strip():
                continue
                
            start_time = time.time()
            asyncio.run(orchestrator.execute_task(task))
            end_time = time.time()
            
            print(f"⏱️  Tiempo de ejecución: {end_time - start_time:.2f} segundos")
            
        except KeyboardInterrupt:
            break
