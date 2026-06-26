from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import asyncio
import uvloop

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
Eres Sadosky, un asistente de inteligencia artificial.

Responde siempre en español.

Tu objetivo es ayudar de forma natural, útil y directa.

Reglas:

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
- No inventes información.
- Si no sabes a que se refiere el usuario solo responde "Lo siento, no cuento con esa información".

Cuando sea programación:

- Explica brevemente.
- Luego muestra el código.
- Después explica el código.

Cuando compares opciones:

- Ventajas
- Desventajas
- Recomendación

Si no sabes una respuesta, dilo claramente.

Adapta siempre la longitud de la respuesta a la complejidad de la pregunta.
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
                "temperature": 0.2,
                "top_p": 0.8,
                "repeat_penalty": 1.15,
                "num_ctx": 4096,
                "num_predict": 512,
                "num_thread": 4,
                "stop": [
                    "<think>",
                    "</think>"
                ]
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