from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import asyncio
import uvloop
import threading
import requests
import json

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI()

# =====================================
# CONFIGURACIÓN
# =====================================

MODELO = "phi3:mini"

MAX_USUARIOS = 3
semaforo = threading.Semaphore(MAX_USUARIOS)

# =====================================
# CORS
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================
# PROMPT
# =====================================

SYSTEM_PROMPT = """
- Si una respuesta puede escribirse como texto normal, nunca uses ```.


Cuando compares opciones:

- Ventajas
- Desventajas
- Recomendación

Si no sabes una respuesta, dilo claramente.

Adapta siempre la longitud de la respuesta a la complejidad de la pregunta.
"""

# =====================================
# MODELO
# =====================================

class Consulta(BaseModel):
    mensaje: str

# =====================================
# API
# =====================================

@app.get("/")
def inicio():
    return {
        "estado": "API funcionando"
    }

# =====================================
# CHAT
# =====================================

@app.post("/chat")
def chat(consulta: Consulta):

    if not semaforo.acquire(blocking=False):
        raise HTTPException(
            status_code=429,
            detail="Servidor ocupado. Intente nuevamente."
        )

    try:

        respuesta = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODELO,
                "system": SYSTEM_PROMPT,
                "prompt": consulta.mensaje,
                "stream": True,
                "keep_alive": "1h",
                "options": {
                    "temperature": 0.45,
                    "top_p": 0.92,
                    "top_k": 40,
                    "repeat_penalty": 1.15,
                    "num_ctx": 4096,
                    "num_predict": 600,
                    "num_thread": 4,
                    "stop": [
                        "<think>",
                        "</think>"
                    ]
                }
            },
            stream=True,
            timeout=300
        )

        respuesta.raise_for_status()

        def generar():

            for linea in respuesta.iter_lines():

                if not linea:
                    continue

                try:
                    dato = json.loads(linea.decode("utf-8"))

                    if "response" in dato:
                        yield dato["response"]

                    if dato.get("done", False):
                        break

                except json.JSONDecodeError:
                    continue

        return StreamingResponse(
            generar(),
            media_type="text/plain; charset=utf-8"
        )

    except requests.exceptions.RequestException as e:

        raise HTTPException(
            status_code=500,
            detail=f"No se pudo conectar con Ollama: {e}"
        )

    finally:

        semaforo.release()