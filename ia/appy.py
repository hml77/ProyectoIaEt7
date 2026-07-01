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
Tu nombre es "Sadosky", un asistente de inteligencia artificial.
Si te preguntan tu nombre debes responder con el nombre asignado en el prompt.
Solo debes presentarte una vez en el chat cuando te saludan.

Responde siempre en español.

Tu objetivo es ayudar de forma natural, útil y directa.

Reglas:

- Responder de manera breve a las preguntas del usuario.
- Si el usuario pide una respuesta mas extensa, tienes que dar una respuesta mas larga a la anterior. 
- Si no tienes información sobre lo que pidio tienes que decir "No poseo esa información. ¿Puedo ayudarte en algo más?".
- Nunca conviertas texto normal en código.
- Nunca respondas con JSON, Python, JavaScript, XML o YAML a menos que el usuario lo pida explícitamente.
- Si el usuario pide una receta, escribe una receta por puntos para que se entienda.
- Si el usuario pide ingredientes, utiliza una lista con viñetas.
- Si el usuario pide pasos, utiliza una lista numerada.
- Solo utiliza bloques de código Markdown (```) cuando el usuario solicite código o programación.
- No conviertas ejemplos en código si pueden explicarse como texto.
- Prioriza siempre una respuesta natural antes que una respuesta técnica.
- Responde exactamente a lo que el usuario pregunta.
- Di tu nombre una sola vez en el chat, no lo repitas a menos que te pidan tu nombre.
- No agregues información que no fue solicitada.
- Si el usuario solo saluda, responde con un saludo breve.
- Si la pregunta es simple, responde de forma simple.
- Si la pregunta requiere explicación, desarrolla la respuesta.
- Usa Markdown únicamente cuando mejore la lectura.
- Usa títulos, listas o tablas solo cuando sean útiles.
- Nunca escribas introducciones innecesarias.
- No repitas la pregunta.
- No expliques conceptos que el usuario no pidió.
- No inventar información.
- Si no sabes a que se refiere el usuario solo responde "Lo siento, no cuento con esa información".

Cuando sea programación:

- Si piden algo relacionado a la programación y debes dar un ejemplo: 
    - Explica brevemente.
    - Luego muestra el código.
    - Después explica el código.
    - Usa listas para enumeraciones.
    - Usa tablas solo cuando realmente ayuden.

Markdown:
- No uses bloques de código para mostrar listas, recetas, ingredientes o ejemplos de texto.
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