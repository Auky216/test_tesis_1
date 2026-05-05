import aiohttp

async def query_ollama(sys_prompt: str, context: str, max_tokens: int = 128, temp: float = 0.0) -> str:
    url = "http://127.0.0.1:11434/api/generate"
    
    payload = {
        "model": "qwen2.5-coder:3b",
        "prompt": f"<|im_start|>system\n{sys_prompt}<|im_end|>\n<|im_start|>user\n{context}<|im_end|>\n<|im_start|>assistant\n",
        "stream": False,
        "raw": True,
        "keep_alive": -1, # Mantiene modelo anclado en VRAM/RAM
        "options": {
            "temperature": temp, # Temperatura dinámica
            "num_predict": max_tokens   # Límite configurable
        }
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                return data.get("response", "")
        except aiohttp.ClientError as e:
            print(f"Error conectando con Ollama: {e}")
            return ""
