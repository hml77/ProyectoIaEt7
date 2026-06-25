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

@app.get("/")
def inicio():
    return {"estado": "API funcionando"}

@app.post("/chat")
def chat(consulta: Consulta):

    prompt = f"""
Eres un asistente de inteligencia artificial.

Responde usando este formato
Resumen:
...

Explicacion:
...

Conclucion:
...

Pregunta:
{consulta.mensaje}
"""

    respuesta = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    datos = respuesta.json()

    return {
        "pregunta": consulta.mensaje,
        "respuesta": datos["response"]
    }