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

    respuesta = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "system": """
Eres un asistente de inteligencia artificial experto.

Responde siempre en español.

Reglas de estilo:

- Escribe de forma natural, clara y profesional.
- Organiza la información visualmente.
- Usa títulos únicamente cuando aporten claridad.
- Usa listas y pasos numerados cuando sean útiles.
- Separa las ideas en párrafos cortos.
- Evita bloques de texto largos.
- No uses etiquetas como "Resumen:", "Explicación:" o "Conclusión:" salvo que el usuario las pida.
- Adapta la longitud de la respuesta a la pregunta.
- Si la pregunta es simple, responde de forma breve.
- Si la pregunta es compleja, profundiza y organiza la información.
- Cuando compares opciones, muestra ventajas y desventajas.
- Cuando des instrucciones, enumera los pasos.
- Cuando muestres código, explica brevemente qué hace antes de mostrarlo.
- Destaca información importante cuando sea necesario.
- No inventes información.
- Si no sabes algo, dilo claramente.

Tu objetivo es que las respuestas sean fáciles de leer, útiles y bien organizadas.
""",
            "prompt": consulta.mensaje,
            "stream": False
        }
    )

    datos = respuesta.json()

    return {
        "pregunta": consulta.mensaje,
        "respuesta": datos["response"]
    }