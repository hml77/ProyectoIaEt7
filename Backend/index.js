const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const MODELO = 'llama3';

app.get('/', (req, res) => {
  res.json({ estado: '✅ Backend funcionando correctamente' });
});

app.post('/chat', async (req, res) => {
  const { mensaje } = req.body;

  if (!mensaje) {
    return res.status(400).json({ error: 'Falta el campo mensaje' });
  }

  try {
    const respuestaOllama = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: MODELO,
        prompt: mensaje,
        stream: false
      })
    });

    if (!respuestaOllama.ok) {
      throw new Error('Ollama no respondio correctamente');
    }

    const datos = await respuestaOllama.json();
    res.json({ respuesta: datos.response });

  } catch (error) {
    res.status(500).json({
      error: 'No se pudo conectar con Ollama',
      detalle: error.message
    });
  }
});

app.listen(3000, () => {
  console.log('✅ Backend iniciado correctamente');
  console.log('🌐 Escuchando en http://localhost:3000');
  console.log('🤖 Usando modelo: ' + MODELO);
});
