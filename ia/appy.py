from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Consulta(BaseModel):
    mensaje: str

MODELO = "qwen3:8b"

@app.get("/")
def inicio():
    return {"estado": "API funcionando"}

@app.post("/chat")
def chat(consulta: Consulta):

    try:
        respuesta = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODELO,
                "system": """
Eres un asistente experto.

Responde siempre en español.

Normas de respuesta:

- Responde primero a la pregunta de forma directa.
- Después explica brevemente el motivo.
- Evita introducciones innecesarias.
- Evita frases como "interesante pregunta", "buena pregunta" o similares.
- No repitas información.
- Sé claro, conciso y natural.
- Utiliza listas únicamente cuando aporten claridad.
- Para preguntas simples, responde de forma breve.
- Para preguntas complejas, organiza la información en secciones.
- No inventes información.
- Si la pregunta es hipotética, especifícalo.
- No escribas títulos como "Resumen", "Explicación" o "Conclusión" salvo que el usuario lo pida.

Tu prioridad es responder primero y explicar después.
""",
                "prompt": consulta.mensaje,
                "stream": False
            },
            timeout=120
        )

        respuesta.raise_for_status()

        datos = respuesta.json()

        return {
            "pregunta": consulta.mensaje,
            "respuesta": datos.get("response", "No se recibió respuesta del modelo.")
        }

    except Exception as e:
        print("ERROR:", e)

        return {
            "pregunta": consulta.mensaje,
            "respuesta": f"Error interno: {str(e)}"
        }