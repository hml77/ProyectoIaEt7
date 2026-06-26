from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import requests

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI()

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
# MODELO
# =====================================
MODELO = "phi3:mini"

# =====================================
# PROMPT DEL SISTEMA
# =====================================
SYSTEM_PROMPT = """
Eres EDEN, un asistente de inteligencia artificial.

Responde siempre en español.

Objetivo:
Dar respuestas claras, correctas y fáciles de leer.

Reglas:

- Responde directamente a la pregunta.
- No saludes.
- No uses frases como:
  - Buena pregunta.
  - Excelente consulta.
  - Interesante.
  - Claro.
  - Por supuesto.

Organiza visualmente las respuestas.

Cuando sea útil utiliza:

- ## Títulos
- Listas
- Listas numeradas
- Tablas
- Ejemplos
- Bloques de código Markdown

Nunca escribas enormes bloques de texto.

Divide las ideas en párrafos cortos.

Cuando expliques programación:

1. Explica brevemente la solución.
2. Muestra el código.
3. Explica las partes importantes.

Cuando compares opciones:

- Ventajas
- Desventajas
- Recomendación

No inventes información.

Si no conoces una respuesta, dilo claramente.

Escribe de forma profesional, clara y agradable.
"""

# =====================================
# MODELO DE DATOS
# =====================================
class Consulta(BaseModel):
    mensaje: str

# =====================================
# API
# =====================================
@app.get("/")
def inicio():
    return {"estado": "API funcionando"}

# =====================================
# CHAT
# =====================================
@app.post("/chat")
def chat(consulta: Consulta):

    respuesta = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": MODELO,
            "system": SYSTEM_PROMPT,
            "prompt": consulta.mensaje,
            "stream": True,
            "keep_alive": "1h",
            "options": {
                "temperature": 0.4,
                "top_p": 0.9,
                "num_ctx": 2048,
                "num_predict": 350,
                "num_thread": 4
            }
        },
        stream=True
    )

    def generar():

        for linea in respuesta.iter_lines():

            if linea:

                dato = json.loads(linea.decode())

                if "response" in dato:
                    yield dato["response"]

    return StreamingResponse(
        generar(),
        media_type="text/plain"
    )