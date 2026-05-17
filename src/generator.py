import json
import aiohttp
import re

class CodeGenerator:
    def __init__(self, model_name: str = "qwen2.5-coder:1.5b", ollama_url: str = "http://localhost:11434/api/generate"):
        self.model_name = model_name
        self.ollama_url = ollama_url

    def _extract_python_code(self, text: str) -> str:
        """Extrae el código puro de los bloques de markdown si el modelo responde con ellos."""
        match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()
        
    async def generate_code(self, subtask_desc: str, context: str) -> str:
        """
        Capa 4: Genera código usando Qwen2.5-Coder vía Ollama con estructura fija.
        Suprime razonamiento verbose.
        """
        prompt = f"""ROLE: Expert Python Developer
TASK: {subtask_desc}
REQUIREMENTS: Max 100 lines, maintainability, clean code.
CONSTRAINTS: No verbose reasoning, output ONLY code.
CONTEXT: {context}
GENERATE:"""
        
        print(f"[*] Solicitando inferencia a {self.model_name}...")
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Temperatura baja para código determinista
                "num_predict": -1    # -1 le dice a Ollama: "Usa todos los tokens que necesites hasta terminar"
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ollama_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        raw_response = data.get("response", "")
                        return self._extract_python_code(raw_response)
                    else:
                        error_text = await response.text()
                        print(f"[!] Error de la API de Ollama (Status {response.status}): {error_text}")
                        return "# Error en generación"
        except Exception as e:
            print(f"[!] No se pudo conectar a Ollama en {self.ollama_url}. ¿Está encendido?")
            print(f"[!] Detalles: {e}")
            return f"# Fallback simulado por error de conexión\ndef procesar_{subtask_desc[:5].lower()}():\n    pass\n"

    async def classify_intent(self, user_input: str) -> str:
        """Enrutador: Decide si el usuario quiere código o hacer una pregunta."""
        prompt = f"Evaluate this request: '{user_input}'. Is the user asking to write/generate code, or are they asking a conversational question? Reply strictly with the exact word 'CODE' or 'QUESTION'."
        payload = {"model": self.model_name, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ollama_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        resp = data.get("response", "").upper()
                        if "QUESTION" in resp: return "QUESTION"
        except Exception:
            pass
        return "CODE"

    async def answer_question(self, question: str, context: str) -> str:
        """Genera una respuesta conversacional natural."""
        prompt = f"ROLE: Helpful Assistant.\nCONTEXT (Memory): {context}\nUSER QUESTION: {question}\nRespond naturally in Spanish."
        payload = {"model": self.model_name, "prompt": prompt, "stream": False, "options": {"temperature": 0.4}}
        print(f"[*] Consultando a {self.model_name}...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ollama_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "").strip()
        except Exception as e:
            return f"Error de conexión: {e}"
        return "No pude generar respuesta."
