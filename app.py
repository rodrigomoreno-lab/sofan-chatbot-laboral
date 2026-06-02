"""
SOFAN Chatbot Laboral Inclusivo v3.0
Arquitectura: Meta WhatsApp Cloud API â FastAPI â Claude AI + Tools â Google Sheets
FundaciÃ³n SOFAN Â· Plataforma Laboral Ãuble Â· 2026
"""

import os, json, httpx, re
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
import anthropic
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SOFAN Chatbot Laboral", version="3.0.0")
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
conversaciones: dict[str, list] = {}

META_PHONE_ID = os.getenv("META_PHONE_NUMBER_ID")
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "sofan2026")

# ââ Formateo WhatsApp ââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def limpiar_markdown(texto: str) -> str:
    """Convierte Markdown a formato limpio para WhatsApp."""
    # Eliminar negrita que corta palabras: **S**ituaciÃ³n â SituaciÃ³n
    texto = re.sub(r'\*\*([A-Za-zÃ-Ã¿])\*\*([A-Za-zÃ-Ã¿])', r'\1\2', texto)
    # **texto** â *texto* (negrita WhatsApp)
    texto = re.sub(r'\*\*(.+?)\*\*', r'*\1*', texto)
    # Eliminar # encabezados
    texto = re.sub(r'^#{1,6}\s+', '', texto, flags=re.MULTILINE)
    # Eliminar lÃ­neas horizontales ---
    texto = re.sub(r'^[-*_]{3,}$', '', texto, flags=re.MULTILINE)
    # Limpiar lÃ­neas en blanco mÃºltiples
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto.strip()

# ââ Google Sheets ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def get_sheets():
    creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON", "{}"))
    creds = Credentials.from_service_account_info(
        creds_json, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(creds)
    return gc.open(os.getenv("SHEET_NAME", "Base de Datos - Chatbot Laboral SOFAN 2026"))

# ââ Herramientas MCP âââââââââââââââââââââââââââââââââââââââââââââââââââââââ
TOOLS = [
    {
        "name": "guardar_perfil_usuario",
        "description": "Guarda o actualiza el perfil laboral del usuario en Google Sheets. Ãsala cuando hayas recopilado nombre y al menos 2 datos mÃ¡s.",
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
        "description": "Busca si el usuario ya tiene un perfil guardado. Ãsala al inicio de cada conversaciÃ³n.",
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

SYSTEM_PROMPT = """Eres el orientador/a laboral virtual de la Plataforma Laboral Inclusiva de FundaciÃ³n SOFAN (Ãuble, Chile).
Tu misiÃ³n es acompaÃ±ar a personas con discapacidad en su bÃºsqueda de empleo digno.
Responde SIEMPRE en espaÃ±ol. Frases cortas. Lenguaje cÃ¡lido, inclusivo y NO asistencialista.

FORMATO OBLIGATORIO - MUY IMPORTANTE:
- USA TEXTO PLANO. NUNCA uses **X**palabra (asteriscos que cortan palabras). EstÃ¡ PROHIBIDO.
- Negrita en WhatsApp: *texto* (un asterisco cada lado). Ejemplo: *Hola* no **Hola**
- SIEMPRE ofrece opciones numeradas para que el usuario responda con un nÃºmero.
- Ejemplo correcto de opciones:
  Â¿QuÃ© necesitas hoy?
  1. OrientaciÃ³n laboral
  2. Crear mi perfil
  3. Hacer mi CV
  4. Buscar empleo
- Usa pocos asteriscos. Solo para destacar algo importante.
- Las URLs deben escribirse completas como texto plano (son clickeables automÃ¡ticamente en WhatsApp).

BIENVENIDA (cuando alguien escribe por primera vez o dice "hola"):
Â¡Hola! Soy tu orientador/a laboral de la Plataforma Laboral Inclusiva de FundaciÃ³n SOFAN.

Puedo ayudarte con:
1. OrientaciÃ³n laboral (entrevistas, derechos, Ley 21.015)
2. Crear tu perfil laboral
3. Armar tu CV
4. Buscar ofertas de empleo

Â¿Con quÃ© quieres comenzar? Responde con el nÃºmero.

MÃTODO STAR (sin asteriscos cortando palabras):
SituaciÃ³n: describe el contexto...
Tarea: explica el desafÃ­o...
AcciÃ³n: cuenta lo que hiciste...
Resultado: menciona el logro...

MÃDULOS:
1. ORIENTACIÃN LABORAL: entrevistas, mÃ©todo STAR, Ley 21.015, SENADIS, OMIL, ajustes razonables.
2. PERFIL LABORAL: recopila nombre, telÃ©fono, email, ciudad, educaciÃ³n, experiencia, habilidades, Ã¡rea interÃ©s, disponibilidad (uno a la vez, siempre con opciones numeradas).
3. CV (formato SOFAN 2026): datos personales, perfil, experiencia, formaciÃ³n, cursos, habilidades.
4. PORTALES DE EMPLEO (en este orden):
   - https://sof-ia.cl/ (Plataforma Laboral Inclusiva SOFAN - mencionar SIEMPRE primero)
   - https://www.bne.cl/ (Bolsa Nacional de Empleo - mencionar segundo)
   - www.incluyeme.com
   - www.empleospublicos.cl
   - www.computrabajo.cl
   Entrega siempre las URLs completas como texto plano.

HORAS SEMANALES - Ley 21.561 (40 horas):
- Desde abril 2026: mÃ¡ximo 42 horas semanales (VIGENTE AHORA)
- Desde abril 2028: serÃ¡ mÃ¡ximo 40 horas semanales
- Informa siempre que el lÃ­mite actual es 42 horas semanales.

CERTIFICADO DE DISCAPACIDAD - Ley 21.015:
- El certificado DEBE estar VIGENTE para acceder a cupos de inclusiÃ³n laboral.
- Un certificado VENCIDO NO habilita para los cupos de la Ley 21.015.
- Si el usuario tiene certificado vencido: indicar que debe renovarlo en COMPIN o SENADIS ANTES de postular a cupos de la Ley 21.015.
- Opciones a presentar:
  1. Tengo certificado vigente
  2. Mi certificado estÃ¡ vencido (necesito renovarlo)
  3. Estoy en proceso de obtenerlo
  4. No tengo certificado
  5. Prefiero no decir

HERRAMIENTAS: usa obtener_perfil_usuario al inicio, guardar_perfil_usuario cuando tengas nombre+2 datos, registrar_conversacion tras respuestas importantes.
Si el mensaje es largo, avisa que continuarÃ¡s en el siguiente mensaje.
NUNCA uses lenguaje asistencialista. Trata a la persona como profesional capaz."""

async def enviar_whatsapp(telefono: str, mensaje: str):
    """EnvÃ­a mensaje via Meta WhatsApp Cloud API."""
    token = os.getenv("META_ACCESS_TOKEN")
    phone_id = os.getenv("META_PHONE_NUMBER_ID")
    url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
    mensaje_limpio = limpiar_markdown(mensaje)
    partes = [mensaje_limpio[i:i+1500] for i in range(0, len(mensaje_limpio), 1500)]
    async with httpx.AsyncClient() as client:
        for parte in partes:
            r = await client.post(url,
                headers={"Authorization": f"Bearer {token}",
                         "Content-Type": "application/json"},
                json={"messaging_product": "whatsapp", "to": telefono,
                      "type": "text", "text": {"body": parte}})
            if r.status_code != 200:
                print(f"[SEND ERROR] {r.status_code}: {r.text[:200]}")

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

    return "Lo siento, hubo un error. Por favor escribe de nuevo. ð"

# ââ Endpoints ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
@app.get("/webhook")
async def verificar_webhook(request: Request):
    params = dict(request.query_params)
    if (params.get("hub.mode") == "subscribe" and
            params.get("hub.verify_token") == META_VERIFY_TOKEN):
        return PlainTextResponse(params.get("hub.challenge", ""))
    return Response(status_code=403)

@app.post("/webhook")
async def recibir_mensaje(request: Request):
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
        elif tipo == "audio":
            media_id = msg.get("audio", {×ÒÙ]
YB[
ÐUQS×HÝ[YÛßNYYXWÚY^ÛYYXWÚYHB]ØZ][X\ÝÚ]Ø\
[YÛËXÚX°ëHH]Y[È<'ã¦{î#ÈÜZÜHÛÛÈØÙ\ÛÈ^Ë°¯ÔYY\È\ØÜX\YHHY[ØZOÈH\ÜÛÈH[YYX]ËB]\ÈÝ]\ÈÚÈB[Y\ÈOH[\XÝ]H^ÈH
\ÙËÙ]
[\XÝ]HßJBÙ]
]ÛÜ\HßJKÙ]
]HJB[ÙN]ØZ][X\ÝÚ]Ø\
[YÛËXÚX°ëHHY[ØZKÜZÜHÛÛÈØÙ\ÛÈ^Ë°¯ÔYY\È\ØÜX\YHÈ]YHXÙ\Ú]\ÏÈB]\ÈÝ]\ÈÚÈBYÝ^Î]\ÈÝ]\ÈÚÈB[
ÓTÑ×HÝ[YÛßNÝ^ÖÎ_HB\ÜY\ÝHHØ[\Ü\ÜY\ÝWØÛ]YJ[YÛË^ÊB]ØZ][X\ÝÚ]Ø\
[YÛË\ÜY\ÝJB^Ù\^Ù\[Û\ÈN[
ÑTÔHÙ_HB]\ÈÝ]\ÈÚÈB\Ù]
ÚX[B\Þ[ÈYX[

N]\ÈÝ]\ÈÚÈÙ\XÙHÓÑSÚ]ÝXÜ[È\ÝX\[Ü×ØXÝ]ÜÈ[ÛÛ\ØXÚ[Û\Ê_B\Ù]
ÈB\Þ[ÈYÛÝ

N]\ÈY[ØZHÓÑSÚ]ÝXÜ[ÈHY]HÛÝYTHX[ÚX[BY×Û[YW×ÈOH×ÛXZ[×È[\Ü]XÛÜ]XÛÜ[\\ÜÝHÜZ[
ÜËÙ][Ô
JJB
