from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class Consulta(BaseModel):
    mensaje: str

@app.get("/")
def inicio():
    return {"estado": "API funcionando"}

@app.post("/chat")
def chat(consulta: Consulta):

    prompt = f"""
Eres un asistente de inteligencia artificial.

Responde en español.
Sé claro y directo.
No inventes información.
Si la pregunta es ambigua, explica cómo la interpretas.
no respondas de manera extensa, a no ser que el usuario lo solicite.

Pregunta:
{consulta.mensaje}
"""

    respuesta = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False
        }
    )

    datos = respuesta.json()

    return {
        "pregunta": consulta.mensaje,
        "respuesta": datos["response"]
    }