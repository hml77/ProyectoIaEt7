from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# ==========================
# CORS
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# Modelo
# ==========================
MODELO = "qwen3:8b"

# ==========================
# Prompt del sistema
# ==========================
SYSTEM_PROMPT = """
Eres EDEN, un asistente de inteligencia artificial.

Responde siempre en español.

Tu estilo debe ser claro, profesional y agradable de leer.

Reglas:

- Responde directamente a la pregunta.
- No saludes.
- No uses frases como:
  - Buena pregunta.
  - Excelente consulta.
  - Interesante.
  - Claro.
  - Por supuesto.
  - Entendido.

Organiza las respuestas de forma visual.

Cuando sea útil:

- Usa títulos Markdown (##)
- Usa listas
- Usa listas numeradas
- Usa tablas
- Usa ejemplos
- Usa bloques de código Markdown

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

Cuando una respuesta sea sencilla, responde de forma breve.

Cuando el usuario pida una explicación completa, desarrolla el tema.

No inventes información.

Si no sabes algo, dilo claramente.

No utilices emojis a menos que el usuario los pida.

Escribe de forma natural, parecida a ChatGPT.
"""

# ==========================
# Modelo de datos
# ==========================
class Consulta(BaseModel):
    mensaje: str

# ==========================
# Ruta principal
# ==========================
@app.get("/")
def inicio():
    return {"estado": "API funcionando"}

# ==========================
# Chat
# ==========================
@app.post("/chat")
def chat(consulta: Consulta):

    try:

        respuesta = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODELO,
                "system": SYSTEM_PROMPT,
                "prompt": consulta.mensaje,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            },
            timeout=180
        )

        respuesta.raise_for_status()

        datos = respuesta.json()

        return {
            "pregunta": consulta.mensaje,
            "respuesta": datos.get(
                "response",
                "No se obtuvo respuesta del modelo."
            )
        }

    except requests.exceptions.RequestException as e:
        return {
            "pregunta": consulta.mensaje,
            "respuesta": f"Error al conectar con Ollama: {e}"
        }

    except Exception as e:
        return {
            "pregunta": consulta.mensaje,
            "respuesta": f"Error interno del servidor: {e}"
        }