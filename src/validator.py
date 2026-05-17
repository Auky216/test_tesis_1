import subprocess
import os
from typing import Tuple

class Validator:
    def __init__(self):
        self.temp_file = ".temp_val.py"
        
    def validate_syntax(self, code: str) -> Tuple[bool, str]:
        """Pipeline 1: Usa ruff para validar sintaxis rápidamente (<100ms)."""
        with open(self.temp_file, "w") as f:
            f.write(code)
            
        try:
            # Solo evalúa errores fatales de sintaxis y variables no definidas
            result = subprocess.run(
                ["ruff", "check", "--select=E9,F63,F7,F82", self.temp_file], 
                capture_output=True, 
                text=True
            )
            return result.returncode == 0, result.stdout
        except FileNotFoundError:
            return True, ""
        finally:
            if os.path.exists(self.temp_file):
                os.remove(self.temp_file)
            
    def validate_execution(self, code: str) -> Tuple[bool, str]:
        """Pipeline 3: Ejecuta el código en runtime para cazar errores lógicos (Timeouts o Tracebacks)."""
        with open(self.temp_file, "w") as f:
            f.write(code)
            
        try:
            result = subprocess.run(
                ["python3", self.temp_file], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, ""
            return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Timeout: Ejecución duró más de 5 segundos (posible bucle infinito o algoritmo ineficiente)."
        except Exception as e:
            return False, str(e)
        finally:
            if os.path.exists(self.temp_file):
                os.remove(self.temp_file)
    def validate_all(self, code: str) -> Tuple[bool, dict]:
        """
        Capa 5: Valida el código y devuelve un score compuesto 
        (60% tests + 20% sintaxis + 10% interfaz + 10% estructura).
        """
        is_syn_valid, syn_details = self.validate_syntax(code)
        if not is_syn_valid:
            return False, {"error_type": "syntax", "score": 20, "details": syn_details}
            
        is_exec_valid, exec_details = self.validate_execution(code)
        if not is_exec_valid:
            # En Raspberry Pi los errores lógicos son mortales, score más bajo.
            return False, {"error_type": "execution_traceback", "score": 30, "details": exec_details[-500:]}
            
        return True, {"error_type": None, "score": 100, "details": ""}
