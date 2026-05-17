from typing import List
from models import SubTask

class Planner:
    def __init__(self):
        pass
        
    def decompose_task(self, global_task: str) -> List[SubTask]:
        """
        Capa 3: Para el modo de chat interactivo, procesamos la consulta del usuario
        como una única subtarea directa.
        """
        return [
            SubTask(id="task_dinamica", description=global_task, dependencies=[])
        ]
