"""
SOFAN Chatbot Laboral Inclusivo v3.0
Arquitectura: Meta WhatsApp Cloud API > FastAPI > Claude AI + Tools > Google Sheets
FundaciÃÂ³n SOFAN ÃÂ· Plataforma Laboral ÃÂuble ÃÂ· 2026
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

# Ã¢ÂÂÃ¢ÂÂ Formateo WhatsApp Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
def limpiar_markdown(texto: str) -> str:
    """Convierte Markdown a formato limpio para WhatsApp."""
    # Eliminar negrita que corta palabras: **S**ituaciÃÂ³n = Situacion
    texto = re.sub(r'\*\*([A-Za-zÃÂ-ÃÂ¿])\*\*([A-Za-zÃÂ-ÃÂ¿])', r'\1\2', texto)
    # **texto** -> *texto* (negrita WhatsApp)
    texto = re.sub(r'\*\*(.+?)\*\*', r'*\1*', texto)
    # Eliminar # encabezados
    texto = re.sub(r'^#{1,6}\s+', '', texto, flags=re.MULTILINE)
    # Eliminar lÃÂ­neas horizontales ---
    texto = re.sub(r'^[-*_]{3,}$', '', texto, flags=re.MULTILINE)
    # Limpiar lÃÂ­neas en blanco mÃÂºltiples
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto.strip()

# Ã¢ÂÂÃ¢ÂÂ Google Sheets Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
def get_sheets():
    creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON", "{}"))
    creds = Credentials.from_service_account_info(
        creds_json, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(creds)
    return gc.open(os.getenv("SHEET_NAME", "Base de Datos - Chatbot Laboral SOFAN 2026"))

# Ã¢ÂÂÃ¢ÂÂ Herramientas MCP Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
TOOLS = [
    {
        "name": "guardar_perfil_usuario",
        "description": "Guarda o actualiza el perfil laboral del usuario en Google Sheets. ÃÂsala cuando hayas recopilado nombre y al menos 2 datos mÃÂ¡s.",
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
        "description": "Busca si el usuario ya tiene un perfil guardado. ÃÂsala al inicio de cada conversaciÃÂ³n.",
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

SYSTEM_PROMPT = """Eres el orientador/a laboral virtual de la Plataforma Laboral Inclusiva de FundaciÃÂ³n SOFAN (ÃÂuble, Chile).
Tu misiÃÂ³n es acompaÃÂ±ar a personas con discapacidad en su bÃÂºsqueda de empleo digno.
Responde SIEMPRE en espaÃÂ±ol. Frases cortas. Lenguaje cÃÂ¡lido, inclusivo y NO asistencialista.

FORMATO OBLIGATORIO - MUY IMPORTANTE:
- USA TEXTO PLANO. NUNCA uses **X**palabra (asteriscos que cortan palabras). EstÃÂ¡ PROHIBIDO.
- Negrita en WhatsApp: *texto* (un asterisco cada lado). Ejemplo: *Hola* no **Hola**
- SIEMPRE ofrece opciones numeradas para que el usuario responda con un nÃÂºmero.
- Ejemplo correcto de opciones:
  ÃÂ¿QuÃÂ© necesitas hoy?
  1. OrientaciÃÂ³n laboral
  2. Crear mi perfil
  3. Hacer mi CV
  4. Buscar empleo
- Usa pocos asteriscos. Solo para destacar algo importante.
- Las URLs deben escrib\ÙHÛÛ\]\ÈÛÛ[È^È[È
ÛÛÛXÚÙXX\È]]Ûpàð¨]XØ[Y[H[Ú]Ð\
KQSSQH
ÝX[È[ÝZY[\ØÜXHÜ[Y\H^ÈXÙHÛHN°à° RÛHHÛÞHHÜY[YÜØHXÜ[HH]YÜXHXÜ[[Û\Ú]HH[XÚpàð¬ÛÓÑSYYÈ^]Y\HÛÛKÜY[XÚpàð¬ÛXÜ[
[]\Ý\Ë\XÚÜË^HKMJBÜX\H\[XÜ[Ë\X\HÕ\ØØ\Ù\\ÈH[\[Âðà°¯ÐÛÛ]pàð¨\]ZpàðªY\\ÈÛÛY[\È\ÜÛHÛÛ[°àð®Y\Ëpàð¢UÑÈÕTÛÛ^Î\ØÜXH[ÛÛ^Ë\XN^XØH[\ØY°àð«[ËXØÚpàð¬ÛÝY[HÈ]YHXÚ\ÝK\Ý[YÎY[Ú[ÛH[ÙÜËpàð¤ÑSÔÎKÔQSPÒpàð¤ÓPÔS[]\Ý\Ëpàðª]ÙÈÕT^HKMKÑSQTËÓRSZ\Ý\È^ÛX\ËTSPÔSXÛÜ[HÛXK[0àðªYÛË[XZ[Ú]YYYXØXÚpàð¬Û^\Y[ÚXKX[YY\Ë0àð¨\XH[\°àðª\Ë\ÜÛX[YY
[ÈHH^ÚY[\HÛÛÜÚ[Û\È[Y\Y\ÊKËÕ
ÜX]ÈÓÑSN]ÜÈ\ÛÛ[\Ë\[^\Y[ÚXKÜXXÚpàð¬ÛÝ\ÛÜËX[YY\ËÔSTÈHSTSÈ
[\ÝHÜ[NHÎËÜÛÙZXKÛÈ
]YÜXHXÜ[[Û\Ú]HÓÑSHY[Ú[Û\ÒQSTH[Y\ÊBHÎËÝÝÝËKÛÈ
ÛØHXÚ[Û[H[\[ÈHY[Ú[Û\ÙYÝ[ÊBHÝÝË[Û^Y[YKÛÛBHÝÝË[\[ÜÜXXÛÜËÛHÝÝËÛÛ\]XZËÛ[YØHÚY[\H\ÈTÈÛÛ\]\ÈÛÛ[È^È[ËÔTÈÑSPSSTÈH^HKMH

Ü\ÊNH\ÙHX[pàð¨^[[È
Ü\ÈÙ[X[[\È
QÑSHRÔJBH\ÙHX[Ù\°àð¨Hpàð¨^[[È
Ü\ÈÙ[X[[\ÂH[ÜXHÚY[\H]YH[0àð«[Z]HXÝX[\È
Ü\ÈÙ[X[[\ËÑTQPÐQÈHTÐÐTPÒQQH^HKMNH[Ù\YXØYÈPH\Ý\QÑSH\HXØÙY\HÝ\ÜÈH[Û\Úpàð¬ÛXÜ[H[Ù\YXØYÈSÒQÈÈX[]H\HÜÈÝ\ÜÈHH^HKMKHÚH[\ÝX\[ÈY[HÙ\YXØYÈ[ÚYÎ[XØ\]YHXH[Ý\È[ÓÓTSÈÑSQTÈSTÈHÜÝ[\HÝ\ÜÈHH^HKMKHÜÚ[Û\ÈH\Ù[\K[ÛÈÙ\YXØYÈYÙ[BZHÙ\YXØYÈ\Ý0àð¨H[ÚYÈ
XÙ\Ú]È[Ý\ÊBË\ÝÞH[ØÙ\ÛÈHØ[\Â
È[ÛÈÙ\YXØYÂ
KYY\ÈÈXÚ\TSRQSTÎ\ØHØ[\Ü\[Ý\ÝX\[È[[XÚ[ËÝX\\Ü\[Ý\ÝX\[ÈÝX[È[Ø\ÈÛXJÌ]ÜËYÚ\Ý\ØÛÛ\ØXÚ[Û\È\ÜY\Ý\È[\Ü[\ËÚH[Y[ØZH\È\ÛË]\ØH]YHÛÛ[X\°àð¨\È[[ÚYÝZY[HY[ØZKSÐH\Ù\È[ÝXZH\Ú\Ý[ÚX[\ÝK]HHH\ÛÛHÛÛ[ÈÙ\Ú[Û[Ø\^\Þ[ÈY[X\ÝÚ]Ø\
[YÛÎÝY[ØZNÝN[°àð«XHY[ØZHXHY]HÚ]Ð\ÛÝYTKÚÙ[HÜËÙ][QUWÐPÐÑTÔ×ÕÒÑSBÛWÚYHÜËÙ][QUWÔÓWÓSPTÒQB\HÎËÙÜ\XÙXÛÚËÛÛKÝNKÞÜÛWÚYKÛY\ÜØYÙ\ÈY[ØZWÛ[\[ÈH[\X\ÛX\ÙÝÛY[ØZJB\\ÈHÛY[ØZWÛ[\[ÖÚNJÌMLHÜH[[ÙJ[Y[ØZWÛ[\[ÊKML
WB\Þ[ÈÚ]\Þ[ÐÛY[

H\ÈÛY[Ü\H[\\ÎH]ØZ]ÛY[ÜÝ
\XY\Ï^È]]Ü^][ÛX\\ÝÚÙ[HÛÛ[U\H\XØ][ÛÚÛÛKÛÛ^ÈY\ÜØYÚ[×ÜÙXÝÚ]Ø\È[YÛË\H^^ÈÙH\__JBYÝ]\×ØÛÙHOH[
ÔÑSTÔHÜÝ]\×ØÛÙ_NÜ^Î_HBYØ[\Ü\ÜY\ÝWØÛ]YJ[YÛÎÝY[ØZNÝHOÝY[YÛÈÝ[ÛÛ\ØXÚ[Û\ÎÛÛ\ØXÚ[Û\ÖÝ[YÛ×HH×BÛÛ\ØXÚ[Û\ÖÝ[YÛ×K\[
ÈÛH\Ù\ÛÛ[Y[ØZ_JB\ÝÜX[HÛÛ\ØXÚ[Û\ÖÝ[YÛ×VËLBÜÈ[[ÙJ
JN\ÜHÛ]YKY\ÜØYÙ\ËÜX]J[Ù[HÛ]YK\ÛÛ]MLL
LMX^ÝÚÙ[ÏLLÞ\Ý[OTÖTÕSWÔÓTÛÛÏUÓÓËY\ÜØYÙ\ÏZ\ÝÜX[
BY\ÜÝÜÜX\ÛÛOHÛÛÝ\ÙH\ÝÜX[\[
ÈÛH\ÜÚ\Ý[ÛÛ[\ÜÛÛ[JB\Ý[YÜÈH×BÜÜ]YH[\ÜÛÛ[YÜ]YK\HOHÛÛÝ\ÙH\Ý[YÈHZXÝ]\Ú\[ZY[JÜ]YK[YKÜ]YK[]
B\Ý[YÜË\[
È\HÛÛÜ\Ý[ÛÛÝ\ÙWÚYÜ]YKYÛÛ[ÛÛ[\Ê\Ý[YË[Ý\WØ\ØÚZOQ[ÙJ_JB\ÝÜX[\[
ÈÛH\Ù\ÛÛ[\Ý[YÜßJB[ÙN^ÈHÚ[^Ü[\ÜÛÛ[Y\Ø]^JB\ÝÜX[\[
ÈÛH\ÜÚ\Ý[ÛÛ[^ßJBÛÛ\ØXÚ[Û\ÖÝ[YÛ×HH\ÝÜX[]\^ËÝ\

B]\ÈÚY[ËXÈ[\ÜÜ]Ü\ØÜXHHY]Ë\Ù]
ÝÙXÛÚÈB\Þ[ÈY\YXØ\ÝÙXÛÚÊ\]Y\Ý\]Y\Ý
N\[\ÈHXÝ
\]Y\Ý]Y\WÜ\[\ÊBY
\[\ËÙ]
X[ÙHHOHÝXØÜXH[\[\ËÙ]
X\YWÝÚÙ[HOHQUWÕTQWÕÒÑSN]\Z[^\ÜÛÙJ\[\ËÙ]
XÚ[[ÙHJB]\\ÜÛÙJÝ]\×ØÛÙOMÊB\ÜÝ
ÝÙXÛÚÈB\Þ[ÈYXÚX\ÛY[ØZJ\]Y\Ý\]Y\Ý
NNÙHH]ØZ]\]Y\ÝÛÛ
B[HHÙKÙ]
[HÞßWJVÌBÚ[Ù\ÈH[KÙ]
Ú[Ù\ÈÞßWJVÌB[YHHÚ[Ù\ËÙ]
[YHßJBY\ÜØYÙ\ÈH[YKÙ]
Y\ÜØYÙ\È×JBYÝY\ÜØYÙ\Î]\ÈÝ]\ÈÚÈB\ÙÈHY\ÜØYÙ\ÖÌB[YÛÈH\ÙËÙ]
ÛHB\ÈH\ÙËÙ]
\HBY\ÈOH^^ÈH\ÙËÙ]
^ßJKÙ]
ÙHB[Y\ÈOH]Y[ÈYYXWÚYH\ÙËÙ]
]Y[ÈßJKÙ]
YB[
ÐUQS×HÝ[YÛßNYYXWÚY^ÛYYXWÚYHB]ØZ][X\ÝÚ]Ø\
[YÛËXÚXHH]Y[ËÜZÜHÛÛÈØÙ\ÛÈ^Ë\ØÜXHHY[ØZHHH\ÜÛÈH[YYX]ËB]\ÈÝ]\ÈÚÈB[Y\ÈOH[\XÝ]H^ÈH
\ÙËÙ]
[\XÝ]HßJBÙ]
]ÛÜ\HßJKÙ]
]HJB[ÙN]ØZ][X\ÝÚ]Ø\
[YÛËXÚXHHY[ØZKÜZÜHÛÛÈØÙ\ÛÈ^Ë\ØÜXHÈ]YHXÙ\Ú]\ÈHH\ÜÛËB]\ÈÝ]\ÈÚÈBYÝ^Î]\ÈÝ]\ÈÚÈB[
ÓTÑ×HÝ[YÛßNÝ^ÖÎ_HB\ÜY\ÝHHØ[\Ü\ÜY\ÝWØÛ]YJ[YÛË^ÊB]ØZ][X\ÝÚ]Ø\
[YÛË\ÜY\ÝJB^Ù\^Ù\[Û\ÈN[
ÑTÔHÙ_HB]\ÈÝ]\ÈÚÈB\Ù]
ÚX[B\Þ[ÈYX[

N]\ÈÝ]\ÈÚÈÙ\XÙHÓÑSÚ]ÝXÜ[È\ÝX\[Ü×ØXÝ]ÜÈ[ÛÛ\ØXÚ[Û\Ê_B\Ù]
ÈB\Þ[ÈYÛÝ

N]\ÈY[ØZHÓÑSÚ]ÝXÜ[ÈHY]HÛÝYTHX[ÚX[BY×Û[YW×ÈOH×ÛXZ[×È[\Ü]XÛÜ]XÛÜ[\\ÜÝHÜZ[
ÜËÙ][Ô
JJB
