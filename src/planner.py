import json
import aiohttp
from typing import List
from models import SubTask

class Planner:
    def __init__(self, model_name="qwen2.5-coder:1.5b", ollama_url="http://localhost:11434/api/generate"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        
    async def decompose_task(self, global_task: str) -> List[SubTask]:
        """
        Capa 3: Divide la tarea en subtareas más pequeñas consultando al LLM.
        """
        print("[PLANIFICADOR] Descomponiendo la tarea en pasos lógicos...")
        prompt = f"""Break down this programming task into 2 or 3 atomic steps.
Task: {global_task}
Respond STRICTLY with a JSON array of strings representing the steps in English or Spanish. Example: ["Create Node class", "Create insert method"]"""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1, "num_predict": 150}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ollama_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        try:
                            steps = json.loads(data.get("response", "[]"))
                        except:
                            steps = []
                            
                        if isinstance(steps, dict):
                            steps = list(steps.values())
                        elif not isinstance(steps, list):
                            steps = [str(steps)]
                            
                        subtasks = []
                        for i, step in enumerate(steps):
                            if isinstance(step, str) and step.strip():
                                deps = [f"sub_{i}"] if i > 0 else []
                                subtasks.append(SubTask(id=f"sub_{i+1}", description=step, dependencies=deps))
                        
                        if subtasks:
                            print(f"[PLANIFICADOR] Tarea dividida en {len(subtasks)} pasos.")
                            return subtasks
        except Exception as e:
            print(f"[!] Error en planificador: {e}")
            
        print("[PLANIFICADOR] Fallback: Ejecutando como tarea única por seguridad.")
        return [SubTask(id="task_dinamica", description=global_task, dependencies=[])]
