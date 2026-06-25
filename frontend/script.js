// ============================================================
// ⚠️ ÚNICA COSA QUE TENÉS QUE CAMBIAR:
// Cuando el equipo servidor te dé la IP, reemplazala acá abajo
// Ejemplo: const IP_SERVIDOR = "192.168.1.105";
// ============================================================
alert("ESTE ES EL SCRIPT DE /var/www/html");
alert("ESTE ES EL SCRIPT DE frontend");
const IP_SERVIDOR = "192.168.0.100";
const URL_BACKEND = "http://192.168.0.100:8000/chat";

// ============================================================
// MEMORIA DE CHATS
// chats = array de conversaciones guardadas
// chatActual = los mensajes del chat que está abierto ahora
// ============================================================
let chats = JSON.parse(localStorage.getItem("chats") || "[]");
let chatActual = [];
let chatActivoIndex = null; // null = chat nuevo sin guardar todavía

// ============================================================
// VERIFICAR CONEXIÓN AL ARRANCAR
// ============================================================
//async function verificarServidor() {
  //try {
    //const respuesta = await fetch("http://192.168.0.100:8000/");
    //if (respuesta.ok) {
      //document.getElementById("estado-servidor").textContent = "🟢 Servidor En Línea";
      //document.getElementById("estado-servidor").style.background = "#B8D4B0";
    //} else {
      //throw new Error();
    //}
  //} catch {
    //document.getElementById("estado-servidor").textContent = "🔴 Servidor Desconectado";
    //document.getElementById("estado-servidor").style.background = "#E3C3C3";
  //}
//}

//verificarServidor();

// ============================================================
// GUARDAR Y CARGAR CHATS EN EL NAVEGADOR
// ============================================================
function guardarChats() {
  localStorage.setItem("chats", JSON.stringify(chats));
}

function renderizarHistorial() {
  const nav = document.getElementById("historial-chats");
  nav.innerHTML = "";

  if (chats.length === 0) {
    nav.innerHTML = "<p class='sin-chats'>Aún no hay chats guardados</p>";
    return;
  }

  // Mostrar del más reciente al más antiguo
  [...chats].reverse().forEach((chat, indexInvertido) => {
    const indexReal = chats.length - 1 - indexInvertido;

    const item = document.createElement("div");
    item.classList.add("chat-guardado");
    if (indexReal === chatActivoIndex) item.classList.add("activo");

    // Título: primer mensaje del usuario, recortado
    const titulo = chat.titulo || "Chat sin título";

    item.innerHTML = `
      <span class="chat-titulo" onclick="cargarChat(${indexReal})">${titulo}</span>
      <button class="btn-borrar" onclick="borrarChat(${indexReal})">✕</button>
    `;

    nav.appendChild(item);
  });
}

// ============================================================
// NUEVO CHAT
// ============================================================
function nuevoChat() {
  // Si el chat actual tiene mensajes, lo guardamos antes de limpiar
  if (chatActual.length > 0) {
    guardarChatActual();
  }

  // Limpiar pantalla
  chatActual = [];
  chatActivoIndex = null;
  document.getElementById("mensajes-chat").innerHTML = "";
  document.getElementById("mensaje").value = "";
  document.getElementById("pantalla-bienvenida").style.display = "flex";

  renderizarHistorial();
}

function guardarChatActual() {
  // Tomar el primer mensaje del usuario como título
  const primerMensajeUsuario = chatActual.find(m => m.tipo === "usuario");
  const titulo = primerMensajeUsuario
    ? primerMensajeUsuario.texto.slice(0, 35) + (primerMensajeUsuario.texto.length > 35 ? "..." : "")
    : "Chat sin título";

  if (chatActivoIndex !== null) {
    // Actualizar chat existente
    chats[chatActivoIndex] = { titulo, mensajes: chatActual };
  } else {
    // Guardar como nuevo
    chats.push({ titulo, mensajes: chatActual });
    chatActivoIndex = chats.length - 1;
  }

  guardarChats();
}

// ============================================================
// CARGAR UN CHAT ANTERIOR
// ============================================================
function cargarChat(index) {
  // Guardar el chat actual antes de cambiar
  if (chatActual.length > 0 && index !== chatActivoIndex) {
    guardarChatActual();
  }

  chatActivoIndex = index;
  chatActual = [...chats[index].mensajes];

  // Limpiar y redibujar mensajes
  const contenedor = document.getElementById("mensajes-chat");
  contenedor.innerHTML = "";
  document.getElementById("pantalla-bienvenida").style.display = "none";

  chatActual.forEach(({ texto, tipo }) => {
    const burbuja = document.createElement("div");
    burbuja.classList.add("burbuja", tipo);
    burbuja.textContent = texto;
    contenedor.appendChild(burbuja);
  });

  contenedor.scrollTop = contenedor.scrollHeight;
  renderizarHistorial();
}

// ============================================================
// BORRAR UN CHAT DEL HISTORIAL
// ============================================================
function borrarChat(index) {
  chats.splice(index, 1);
  guardarChats();

  // Si borramos el chat que estaba activo, limpiar pantalla
  if (index === chatActivoIndex) {
    chatActual = [];
    chatActivoIndex = null;
    document.getElementById("mensajes-chat").innerHTML = "";
    document.getElementById("pantalla-bienvenida").style.display = "flex";
  } else if (chatActivoIndex !== null && index < chatActivoIndex) {
    chatActivoIndex--;
  }

  renderizarHistorial();
}

// ============================================================
// MOSTRAR MENSAJES EN PANTALLA
// ============================================================
function agregarMensaje(texto, tipo) {
  document.getElementById("pantalla-bienvenida").style.display = "none";

  const contenedor = document.getElementById("mensajes-chat");
  const burbuja = document.createElement("div");
  burbuja.classList.add("burbuja", tipo);

  // Renderizar Markdown
  burbuja.textContent = texto;

  contenedor.appendChild(burbuja);
  contenedor.scrollTop = contenedor.scrollHeight;

  // Guardar el texto original
  chatActual.push({ texto, tipo });
}

function mostrarCargando() {
  document.getElementById("pantalla-bienvenida").style.display = "none";
  const contenedor = document.getElementById("mensajes-chat");
  const burbuja = document.createElement("div");
  burbuja.classList.add("burbuja", "ia", "cargando");
  burbuja.id = "burbuja-cargando";
  burbuja.textContent = "Pensando...";
  contenedor.appendChild(burbuja);
  contenedor.scrollTop = contenedor.scrollHeight;
}

function quitarCargando() {
  const burbuja = document.getElementById("burbuja-cargando");
  if (burbuja) burbuja.remove();
}

// ============================================================
// ENVIAR MENSAJE AL BACKEND
// ============================================================
async function enviarMensaje() {
  const input = document.getElementById("mensaje");
  const texto = input.value.trim();
  if (!texto) return;

  agregarMensaje(texto, "usuario");
  input.value = "";

  document.getElementById("enviar").disabled = true;
  document.getElementById("enviar").textContent = "...";

  mostrarCargando();

  try {
    const respuesta = await fetch(URL_BACKEND, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensaje: texto })
    });

    quitarCargando();

    if (!respuesta.ok) throw new Error("Error del servidor");

    const datos = await respuesta.json();
    agregarMensaje(datos.respuesta, "ia");

  } catch (error) {
    quitarCargando();
    agregarMensaje("❌ No funca maestro", "ia");
    console.error("Error:", error);
  }

  // Guardar automáticamente después de cada respuesta
  guardarChatActual();
  renderizarHistorial();

  document.getElementById("enviar").disabled = false;
  document.getElementById("enviar").textContent = "Enviar";
}

// ============================================================
// EVENTOS
// ============================================================
document.getElementById("enviar").addEventListener("click", enviarMensaje);
document.getElementById("mensaje").addEventListener("keydown", (e) => {
  if (e.key === "Enter") enviarMensaje();
});

// Cargar historial al abrir la página
renderizarHistorial();
// Actualizado lol