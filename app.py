"""
SOFAN Chatbot Laboral Inclusivo
Arquitectura: Meta WhatsApp Cloud API → FastAPI → Claude AI + Tools → Google Sheets
Fundación SOFAN · Plataforma Laboral Ñuble · 2026
"""

import os, json, httpx
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
import anthropic
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SOFAN Chatbot Laboral", version="2.0.0")
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
conversaciones: dict[str, list] = {}

META_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_PHONE_ID = os.getenv("META_PHONE_NUMBER_ID")
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "sofan2026")

# ── Google Sheets ──────────────────────────────────────────────────────────
def get_sheets():
    creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON", "{}"))
    creds = Credentials.from_service_account_info(
        creds_json, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(creds)
    return gc.open(os.getenv("SHEET_NAME", "Base de Datos - Chatbot Laboral SOFAN 2026"))

# ── Herramientas MCP ───────────────────────────────────────────────────────
TOOLS = [
    {
        "name": "guardar_perfil_usuario",
        "description": "Guarda o actualiza el perfil laboral del usuario en Google Sheets. Úsala cuando hayas recopilado nombre y al menos 2 datos más.",
        "input_schema": {
            "type": "object",
            "properties": {
                "telefono":           {"type": "string"},
                "nombre":             {"type": "string"},
                "email":              {"type": "string"},
                "ciudad":             {"type": "string"},
                "region":             {"type": "string"},
                "nivel_educacion":    {"type": "string"},
                "carrera":            {"type": "string"},
                "experiencia":        {"type": "string"},
                "habilidades":        {"type": "string"},
                "area_interes":       {"type": "string"},
                "disponibilidad":     {"type": "string"},
                "certificado_pcd":    {"type": "string"},
                "ajustes_razonables": {"type": "string"},
            },
            "required": ["telefono", "nombre"]
        }
    },
    {
        "name": "obtener_perfil_usuario",
        "description": "Busca si el usuario ya tiene un perfil guardado. Úsala al inicio de cada conversación.",
        "input_schema": {
            "type": "object",
            "properties": {"telefono": {"type": "string"}},
            "required": ["telefono"]
        }
    },
    {
        "name": "registrar_conversacion",
        "description": "Registra intercambios importantes en el log de conversaciones.",
        "input_schema": {
            "type": "object",
            "properties": {
                "telefono":        {"type": "string"},
                "modulo":          {"type": "string"},
                "mensaje_usuario": {"type": "string"},
                "respuesta_bot":   {"type": "string"},
            },
            "required": ["telefono", "modulo", "mensaje_usuario", "respuesta_bot"]
        }
    }
]

def ejecutar_herramienta(nombre: str, params: dict) -> dict:
    try:
        sh = get_sheets()
        if nombre == "guardar_perfil_usuario":
            ws = sh.worksheet("USUARIOS")
            records = ws.get_all_records()
            idx = next((i for i, r in enumerate(records)
                        if str(r.get("ID_CONVERSACION")) == str(params.get("telefono"))), None)
            fila = [datetime.now().strftime("%d/%m/%Y %H:%M"),
                    params.get("telefono",""), params.get("nombre",""),
                    params.get("telefono",""), params.get("email",""),
                    params.get("ciudad",""), params.get("region",""),
                    params.get("nivel_educacion",""), params.get("carrera",""),
                    params.get("experiencia",""), params.get("habilidades",""),
                    params.get("area_interes",""), params.get("disponibilidad",""),
                    params.get("certificado_pcd",""), params.get("ajustes_razonables",""),
                    "whatsapp_meta", "En proceso"]
            if idx is not None:
                ws.update(f"A{idx+2}:Q{idx+2}", [fila])
                return {"status": "actualizado", "nombre": params.get("nombre")}
            else:
                ws.append_row(fila)
                return {"status": "creado", "nombre": params.get("nombre")}

        elif nombre == "obtener_perfil_usuario":
            ws = sh.worksheet("USUARIOS")
            records = ws.get_all_records()
            perfil = next((r for r in records
                           if str(r.get("ID_CONVERSACION")) == str(params.get("telefono"))), None)
            return {"encontrado": True, "perfil": perfil} if perfil else {"encontrado": False}

        elif nombre == "registrar_conversacion":
            ws = sh.worksheet("CONVERSACIONES")
            ws.append_row([datetime.now().strftime("%d/%m/%Y %H:%M"),
                           params.get("telefono",""), params.get("modulo",""),
                           str(params.get("mensaje_usuario",""))[:500],
                           str(params.get("respuesta_bot",""))[:500]])
            return {"status": "registrado"}
    except Exception as e:
        return {"error": str(e)}
    return {"error": "herramienta no reconocida"}

SYSTEM_PROMPT = """Eres el orientador/a laboral virtual de la Plataforma Laboral Inclusiva de Fundación SOFAN (Ñuble, Chile).
Tu misión es acompañar a personas con discapacidad en su búsqueda de empleo digno.
Responde SIEMPRE en español. Frases cortas. Lenguaje cálido e inclusivo.

MÓDULOS:
1. ORIENTACIÓN LABORAL: entrevistas, método STAR, Ley 21.015, SENADIS, OMIL, ajustes razonables.
2. PERFIL LABORAL: recopila nombre, teléfono, email, ciudad, educación, experiencia, habilidades, área interés, disponibilidad (uno a la vez).
3. CV (formato SOFAN 2026): datos personales, perfil, experiencia, formación, cursos, habilidades.
4. OFERTAS: incluyelaboral.cl, incluyeme.com, bne.cl, empleospublicos.cl, computrabajo.cl. Buscar "21.015".

HERRAMIENTAS: usa obtener_perfil_usuario al inicio, guardar_perfil_usuario cuando tengas nombre+2 datos, registrar_conversacion tras respuestas importantes.
Si el mensaje es largo, avisa que continuarás en el siguiente mensaje.
NUNCA uses lenguaje asistencialista. Trata a la persona como profesional."""

async def enviar_whatsapp(telefono: str, mensaje: str):
    """Envía mensaje via Meta WhatsApp Cloud API."""
    url = f"https://graph.facebook.com/v19.0/{META_PHONE_ID}/messages"
    # Dividir mensajes largos
    partes = [mensaje[i:i+1500] for i in range(0, len(mensaje), 1500)]
    async with httpx.AsyncClient() as client:
        for parte in partes:
            await client.post(url,
                headers={"Authorization": f"Bearer {META_TOKEN}",
                         "Content-Type": "application/json"},
                json={"messaging_product": "whatsapp", "to": telefono,
                      "type": "text", "text": {"body": parte}})

def obtener_respuesta_claude(telefono: str, mensaje: str) -> str:
    if telefono not in conversaciones:
        conversaciones[telefono] = []
    conversaciones[telefono].append({"role": "user", "content": mensaje})
    historial = conversaciones[telefono][-20:]

    for _ in range(5):
        resp = claude.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=1000,
            system=SYSTEM_PROMPT, tools=TOOLS, messages=historial)

        if resp.stop_reason == "tool_use":
            historial.append({"role": "assistant", "content": resp.content})
            resultados = []
            for bloque in resp.content:
                if bloque.type == "tool_use":
                    resultado = ejecutar_herramienta(bloque.name, bloque.input)
                    resultados.append({"type": "tool_result", "tool_use_id": bloque.id,
                                       "content": json.dumps(resultado, ensure_ascii=False)})
            historial.append({"role": "user", "content": resultados})
        else:
            texto = "".join(b.text for b in resp.content if hasattr(b, "text"))
            historial.append({"role": "assistant", "content": texto})
            conversaciones[telefono] = historial
            return texto.strip()

    return "Lo siento, hubo un error. Por favor escribe de nuevo. 🙏"

# ── Endpoints ──────────────────────────────────────────────────────────────
@app.get("/webhook")
async def verificar_webhook(request: Request):
    """Verificación del webhook por Meta."""
    params = dict(request.query_params)
    if (params.get("hub.mode") == "subscribe" and
            params.get("hub.verify_token") == META_VERIFY_TOKEN):
        return PlainTextResponse(params.get("hub.challenge", ""))
    return Response(status_code=403)

@app.post("/webhook")
async def recibir_mensaje(request: Request):
    """Recibe mensajes de WhatsApp via Meta Cloud API."""
    try:
        body = await request.json()
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return {"status": "ok"}

        msg = messages[0]
        telefono = msg.get("from", "")
        tipo = msg.get("type", "")

        if tipo == "text":
            texto = msg.get("text", {}).get("body", "")
        elif tipo == "interactive":
            texto = (msg.get("interactive", {})
                     .get("button_reply", {}).get("title", ""))
        else:
            return {"status": "ok"}

        if not texto:
            return {"status": "ok"}

        print(f"[MSG] {telefono}: {texto[:80]}")
        respuesta = obtener_respuesta_claude(telefono, texto)
        await enviar_whatsapp(telefono, respuesta)

    except Exception as e:
        print(f"[ERROR] {e}")

    return {"status": "ok"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "SOFAN Chatbot Laboral v2",
            "usuarios_activos": len(conversaciones)}

@app.get("/")
async def root():
    return {"mensaje": "SOFAN Chatbot Laboral - Meta Cloud API", "health": "/health"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
