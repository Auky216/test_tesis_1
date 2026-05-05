import asyncio
import aiomqtt
import json
import os

STATE_FILE = "latest_telemetry.json"

async def mqtt_listener_loop():
    """
    Background task to listen to Rust telemetry continuously
    and save the latest state to a file.
    """
    while True:
        try:
            async with aiomqtt.Client("127.0.0.1") as client:
                await client.subscribe("iot/telemetry/sensors")
                async for message in client.messages:
                    payload = message.payload.decode()
                    # Caching the latest state
                    with open(STATE_FILE, "w") as f:
                        f.write(payload)
        except Exception as e:
            # Reconexión automática si el broker falla
            await asyncio.sleep(2)

def get_latest_telemetry() -> str:
    """
    Retrieve the latest telemetry from the cache file.
    """
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read()
    return "No telemetry received yet. Hardware might be disconnected."
