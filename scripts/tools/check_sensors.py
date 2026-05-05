import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../python_orchestrator'))
try:
    from state_manager import get_latest_telemetry
    print(get_latest_telemetry())
except Exception as e:
    print(f"Error reading telemetry: {e}")
