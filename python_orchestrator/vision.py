def get_camera_labels() -> str:
    # Simulación de lectura de metadatos de picamera2 (Raspberry Pi AI Camera)
    # En un entorno real, picamera2 procesa el flujo de video en el ISP
    # y devuelve tensores / labels. Solo exponemos los labels para el LLM.
    return "person: 0.95, object_motion: true"
