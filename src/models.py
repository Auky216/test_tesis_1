from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class SubTask:
    id: str
    description: str
    dependencies: List[str]
    code: Optional[str] = None
    status: str = "pending" # pending, generated, validated, failed
    attempts: int = 0

@dataclass
class GlobalState:
    task_description: str
    subtasks: List[SubTask] = field(default_factory=list)
    history: List[Dict] = field(default_factory=list)
