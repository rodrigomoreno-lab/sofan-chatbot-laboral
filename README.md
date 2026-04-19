# 🤝 SOFAN Chatbot Laboral Inclusivo

**Plataforma Laboral Inclusiva · Fundación SOFAN · Ñuble, Chile**

Chatbot de orientación laboral para personas con discapacidad via WhatsApp,
impulsado por Claude AI con herramientas MCP para Google Sheets.

## Arquitectura

```
📱 WhatsApp → Twilio → Render.com (FastAPI) → Claude AI + Tools → 📊 Google Sheets
```

## Módulos del chatbot

| Módulo | Descripción |
|--------|-------------|
| 🧭 Orientación Laboral | Entrevistas, STAR, Ley 21.015, SENADIS |
| 👤 Perfil Laboral | Recopilación de datos laborales |
| 📄 Crear CV | Formato oficial SOFAN 2026 |
| 💼 Ofertas de Trabajo | Portales inclusivos y generales |

## Configuración rápida

### 1. Variables de entorno
```bash
cp .env.example .env
# Editar .env con los valores reales
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar localmente
```bash
uvicorn app:app --reload --port 8000
```

### 4. Desplegar en Render.com
1. Subir carpeta a GitHub (repositorio privado)
2. Conectar repo en render.com → New Web Service
3. Agregar variables de entorno en Render Dashboard
4. Copiar la URL del servicio (ej: `https://sofan-chatbot.onrender.com`)

### 5. Configurar Twilio
1. Twilio Console → Messaging → Try it out → Send a WhatsApp message
2. Sandbox Settings → When a message comes in:
   `https://sofan-chatbot.onrender.com/webhook`
3. Método: HTTP POST

## Estructura de Google Sheets

El archivo debe llamarse exactamente:
**"Base de Datos - Chatbot Laboral SOFAN 2026"**

### Pestaña USUARIOS
Columnas A-Q: FECHA_REGISTRO, ID_CONVERSACION, NOMBRE_COMPLETO, TELEFONO,
EMAIL, CIUDAD, REGION, NIVEL_EDUCACION, CARRERA, EXPERIENCIA, HABILIDADES,
AREA_INTERES, DISPONIBILIDAD, CERTIFICADO_PCD, AJUSTES_RAZONABLES,
MODULO_ACTIVO, ESTADO

### Pestaña CONVERSACIONES
Columnas A-E: FECHA_HORA, ID_CONVERSACION, MODULO, MENSAJE_USUARIO, RESPUESTA_BOT

## Créditos

- IA: Claude Sonnet (Anthropic)
- Mensajería: Twilio WhatsApp Business API
- Base de datos: Google Sheets API v4
- Servidor: FastAPI + Uvicorn en Render.com
- Desarrollado para: Fundación SOFAN, Ñuble, Chile

---
*Versión 1.0 · Abril 2026*
