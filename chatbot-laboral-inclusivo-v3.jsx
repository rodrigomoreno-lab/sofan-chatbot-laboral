import { useState, useRef, useEffect } from "react";

const S = { purple:"#53388C", yellow:"#FBB913", magenta:"#DC0166", purpleL:"#EDE8F7", purpleDk:"#3A2560", bg:"#F4F1FA", white:"#FFFFFF", text:"#1A1030", muted:"#6B6080" };

const MODULES = [
  { id:"orientacion", icon:"🧭", label:"Orientación Laboral",  color:S.purple   },
  { id:"perfil",      icon:"👤", label:"Mi Perfil Laboral",    color:S.purpleDk },
  { id:"cv",          icon:"📄", label:"Crear mi CV",          color:S.magenta  },
  { id:"ofertas",     icon:"💼", label:"Ofertas de Trabajo",   color:"#B7770D"  },
];

const DISABILITY_TYPES = [
  { id:"visual",    label:"Discapacidad Visual",          desc:"Texto grande, descripciones detalladas, sin referencias al color" },
  { id:"auditiva",  label:"Discapacidad Auditiva",        desc:"Todo por texto, sin recomendaciones de llamadas telefónicas" },
  { id:"motora",    label:"Discapacidad Motora / Física", desc:"Botones grandes, preguntas sí/no, mínimo tipeo" },
  { id:"cognitiva", label:"Discapacidad Cognitiva",       desc:"Lenguaje muy simple, un paso a la vez, mucho apoyo visual" },
  { id:"ninguna",   label:"Sin discapacidad específica",  desc:"Configuración estándar, lenguaje fluido" },
];

// MEJORA 2: Regla de abreviaciones — término completo antes de sigla
const ABBR = `REGLA ABREVIACIONES (obligatoria): La primera vez que uses una sigla, escribe SIEMPRE el término completo seguido de la sigla entre paréntesis. Ejemplos: "Persona con Discapacidad (PcD)", "Ley de Inclusión Laboral Nº 21.015 (Ley 21.015)", "Lengua de Señas Chilena (LSCh)", "Servicio Nacional de la Discapacidad (SENADIS)", "Oficina Municipal de Información Laboral (OMIL)", "Servicio Nacional de Capacitación y Empleo (SENCE)", "Comisión de Medicina Preventiva e Invalidez (COMPIN)", "currículum vitae (CV)". Nunca uses una sigla sin haberla definido antes en la misma conversación.`;

// MEJORA 5: Convención ONU 2006
const ONU = `CONVENCIÓN ONU SOBRE DERECHOS DE LAS PERSONAS CON DISCAPACIDAD (2006) — principios que guían TODO tu lenguaje:
• Art. 3a Dignidad y autonomía: trata a la persona como agente activo, no como receptora pasiva de ayuda.
• Art. 3b No discriminación: nunca uses lenguaje que sugiera limitación de capacidades.
• Art. 3c Participación plena: el empleo es un derecho, no un favor.
• Art. 3d Respeto por la diferencia: la discapacidad es diversidad humana, no déficit.
• Art. 6 Igualdad de género: usa lenguaje inclusivo (trabajador/a, candidato/a).
• Art. 9 Accesibilidad: siempre sugiere alternativas accesibles.
• Art. 27 Trabajo digno: menciona ajustes razonables como derecho, no como excepción.
VOCABULARIO CORRECTO: "persona con discapacidad" (no "discapacitado/a"), "persona que usa silla de ruedas" (no "confinado/a"), "persona ciega" (no "invidente"), "persona sorda" (no "sordomudo/a"). Nunca uses "sufre de", "padece", "víctima de".`;

// MEJORA 4: WCAG 2.1 Nivel AAA
const WCAG = `ACCESIBILIDAD WCAG 2.1 AAA en tu comunicación:
• Lectura simple (3.1.5): palabras comunes, oraciones cortas (máx. 20 palabras), estructura clara con viñetas cuando sea necesario.
• Sin dependencia del color (1.4.1): nunca digas "el botón verde" como única instrucción; describe la acción o la posición.
• Alternativas textuales (1.1.1): si mencionas algo visual, descríbelo verbalmente.
• Lenguaje claro (3.1.3): define términos técnicos cuando los uses.
• Consistencia (3.2.4): usa los mismos términos para los mismos conceptos.
• Errores (3.3.1): si el usuario se equivoca, explica amablemente cómo corregir sin culpabilizar.
• Tiempo (2.2): nunca presiones al usuario con urgencia artificial.`;

const BASE_PROMPT = (mod, extraContext = "") => {
  const bases = {
    orientacion: `Eres el orientador/a laboral virtual de la Plataforma Laboral Inclusiva de Fundación SOFAN (Ñuble, Chile). Acompañas a personas con discapacidad en su búsqueda de empleo digno, con enfoque inclusivo, respetuoso y práctico. Responde SIEMPRE en español.

CONTENIDO QUE DOMINAS:
1. PREPARACIÓN PARA ENTREVISTAS: Antes (investigar empresa, repasar currículum vitae (CV), identificar fortalezas/debilidades, llegar 5 min antes). Durante (buena impresión, saludar, no tutear, mirar a los ojos, decir la verdad, mostrar entusiasmo). Sin experiencia: di "estoy disponible para aprender" en vez de "no tengo experiencia". Después: analizar tu desempeño.
2. PREGUNTAS FRECUENTES: "Háblame de ti", "¿Por qué quieres trabajar aquí?", "¿Cuáles son tus fortalezas/debilidades?", "¿Por qué deberíamos contratarte?", "¿Pretensión de renta?"
3. MÉTODO STAR: Situación → Tarea → Acción → Resultado. Explica con ejemplos cotidianos.
4. ENTREVISTA PRESENCIAL vs ONLINE (entrevista por videoconferencia): similitudes y diferencias.
5. HABILIDADES SOCIOEMOCIONALES: asertividad, confianza, empatía, compromiso.
6. DERECHOS LABORALES: Ley de Inclusión Laboral Nº 21.015 (1% de cuota), ajustes razonables, Servicio Nacional de la Discapacidad (SENADIS), Oficina Municipal de Información Laboral (OMIL), Certificado de Discapacidad (COMPIN).

ESTILO: Frases cortas. Valida antes de informar. Termina con pregunta o acción concreta. Nunca asistencialismo.`,

    perfil: `Eres el asistente de perfil laboral de Fundación SOFAN. Recopilas información laboral de forma conversacional, amable y paso a paso. Responde SIEMPRE en español.

INFORMACIÓN A RECOPILAR (en este orden, UN dato a la vez):
1. Nombre completo
2. Teléfono celular
3. Correo electrónico
4. Región y ciudad
5. Nivel educacional (básica / media / técnico / universitario / en curso)
6. Institución y carrera/especialidad (si aplica)
7. Cursos o capacitaciones (Servicio Nacional de Capacitación y Empleo (SENCE), institutos, etc.)
8. Experiencia laboral: empresa, cargo, periodo, funciones. Si no tiene, es completamente válido.
9. Habilidades y conocimientos (computación, idiomas, habilidades blandas)
10. Área de interés laboral
11. Disponibilidad horaria
12. ¿Tiene Certificado de Discapacidad? (opcional, confidencial)
13. ¿Necesita ajustes razonables? (opcional)

REGLAS: Un dato a la vez. Valida con entusiasmo. Al terminar, presenta resumen y pregunta si guardar. Lenguaje simple y valorador.`,

    cv: `Eres el asistente de creación de currículum vitae (CV) de Fundación SOFAN. Usas el formato oficial SOFAN del Taller Apresto Laboral SOFÍA 2026. Responde SIEMPRE en español.
${extraContext ? `\nDATO IMPORTANTE: Esta persona ya completó su perfil laboral. Usa esta información para no pedirle que repita datos:\n${extraContext}\nComienza directamente desde donde falta información para el currículum vitae (CV), no desde el principio.` : ""}

SECCIONES DEL CURRÍCULUM VITAE (CV) SOFAN:
1. DATOS PERSONALES: nombre, teléfono, correo, región/ciudad. NO incluir foto, dirección exacta ni número de identificación tributaria.
2. PERFIL LABORAL: ¿Quién soy? ¿Qué sé hacer? ¿Qué trabajo busco? Adaptar al cargo.
3. EXPERIENCIA LABORAL: empresa, periodo, cargo, funciones. Sin experiencia: mencionar trabajos informales, voluntariados, labores del hogar.
4. FORMACIÓN ACADÉMICA: institución, nivel/carrera, año inicio-término.
5. CURSOS Y CAPACITACIONES: nombre, institución, fecha.
6. HABILIDADES Y CONOCIMIENTOS: computación, idiomas, habilidades blandas.
7. INFORMACIÓN ADICIONAL (opcional): disponibilidad, referencias.

Al final: presenta el currículum vitae (CV) completo en formato texto listo para copiar. Pregunta si también quiere carta de presentación.`,

    ofertas: `Eres el asistente de búsqueda de empleo de Fundación SOFAN. Ayudas a personas con discapacidad a encontrar trabajo real. Responde SIEMPRE en español.

PORTALES RECOMENDADOS:
Especializados en inclusión: incluyelaboral.cl, incluyeme.com, empleosinclusivos.com, pegasconsentido.cl
Generales: bne.cl (Bolsa Nacional de Empleo — más accesible), empleospublicos.cl, trabajando.com, computrabajo.cl, laborum.cl, cl.indeed.com, firstjob.me (primera experiencia)
Empresas que contratan Personas con Discapacidad (PcD): tiendas.empleos.cencosud.com, ripley.trabajando.cl, trabajaenbci.cl, adecco.cl, somosempleo.cl

CONSEJOS: Mismo correo/contraseña en todos los portales. Completar TODOS los apartados del perfil. Escribir "21.015" en el buscador para filtrar empleos de cuota de inclusión. Revisar si los requisitos son excluyentes (obligatorios) u opcionales — si son opcionales, ¡postular igualmente! Constancia: al menos 1 hora diaria de lunes a viernes.

PROCESO: Pregunta tipo de trabajo, región y disponibilidad. Sugiere 2-3 portales relevantes. Explica paso a paso. Motiva a postular aunque no cumpla el 100% de requisitos.`
  };
  return (bases[mod] || "") + "\n\n" + ABBR + "\n\n" + ONU + "\n\n" + WCAG;
};

const DISABILITY_CTX = {
  visual:    `\nACCESIBILIDAD VISUAL (WCAG 1.1.1, 1.3.3): Describe todo verbalmente. Evita referencias al color o posición visual. Enumera pasos: "Primer paso:", "Segundo paso:". Describe cómo navegar sitios web. Prioriza bne.cl que es más accesible. No uses emojis como único portador de información importante.`,
  auditiva:  `\nACCESIBILIDAD AUDITIVA: NUNCA recomiendes llamadas telefónicas. Usa siempre canales escritos: correo electrónico, formularios, aplicación de mensajería WhatsApp. Menciona el derecho a solicitar intérprete de Lengua de Señas Chilena (LSCh) en entrevistas. Ofrece siempre la opción de entrevista por videoconferencia.`,
  motora:    `\nACCESIBILIDAD MOTORA: Haz preguntas de SÍ/NO siempre que puedas. Cuando des opciones, numéralas claramente: "Opción 1:", "Opción 2:". Respuestas cortas. Menciona el derecho a ajustes razonables en el puesto de trabajo (silla ergonómica, software adaptado, etc.).`,
  cognitiva: `\nACCESIBILIDAD COGNITIVA (WCAG 3.1.5): Lenguaje MUY simple. Oraciones de máximo 8 palabras. UN paso a la vez. Usa signos de verificación ✅ para indicar avance. Celebra cada respuesta: "¡Muy bien!" "¡Excelente!". Usa ejemplos de la vida cotidiana. Repite lo importante con otras palabras si es necesario.`,
  ninguna:   "",
};

const QUICK_REPLIES = {
  orientacion: ["¿Cómo me preparo para una entrevista?", "¿Qué es la Ley 21.015?", "¿Qué son los ajustes razonables?", "¿Cómo uso el método STAR?"],
  perfil:      ["Quiero crear mi perfil laboral", "No tengo experiencia laboral", "¿Para qué sirve el perfil?", "Tengo estudios técnicos"],
  cv:          ["Quiero hacer mi currículum vitae (CV)", "Nunca he tenido trabajo formal", "¿Qué pongo en el perfil laboral?", "Quiero carta de presentación"],
  ofertas:     ["¿Qué portales son para inclusión?", "Busco trabajo administrativo", "¿Cómo busco con Ley 21.015?", "¿Qué hago si no cumplo todos los requisitos?"],
};

const INTROS = {
  orientacion: {
    visual:    "¡Bienvenido/a a la Plataforma Laboral Inclusiva de Fundación SOFAN! 👋\n\nLos mensajes están escritos de forma clara y detallada. Todo lo importante está descrito con palabras, sin depender de referencias visuales.\n\nSoy tu orientador/a laboral virtual. ¿Me cuentas tu nombre para comenzar?",
    auditiva:  "¡Hola! 👋 Bienvenido/a a la Plataforma Laboral de Fundación SOFAN.\n\nToda la comunicación es por texto. No te pediré hacer llamadas telefónicas ✅\n\nEstoy aquí para ayudarte a encontrar trabajo digno.\n\n¿Cuál es tu nombre?",
    motora:    "¡Hola! Bienvenido/a a Fundación SOFAN. 👋\n\nHaré preguntas cortas. Cuando pueda, te daré opciones numeradas para que no tengas que escribir mucho.\n\n¿Cuál es tu nombre?",
    cognitiva: "¡HOLA! 👋\n\nSoy tu AYUDANTE para encontrar TRABAJO ✅\n\nVamos PASO A PASO. ¡Es muy fácil!\n\n¿Cuál es tu NOMBRE? ✍️",
    ninguna:   "¡Hola! Bienvenido/a a la Plataforma Laboral Inclusiva de Fundación SOFAN. 👋\n\nEstoy aquí para orientarte en tu búsqueda de empleo en la Región de Ñuble y todo Chile.\n\n¿Cuál es tu nombre para comenzar?",
  },
  perfil: {
    ninguna: "¡Vamos a crear tu perfil laboral! 👤\n\nTe haré preguntas una a la vez para conocerte mejor y conectarte con las mejores oportunidades.\n\n¿Cuál es tu nombre completo?",
    visual:  "¡Vamos a crear tu perfil laboral! 👤\n\nPreguntas detalladas, una a la vez. Comenzamos.\n\n¿Cuál es tu nombre completo?",
    auditiva:"¡Perfil laboral! 👤\n\nPreguntas por texto, una a la vez ✅\n\n¿Cuál es tu nombre completo?",
    motora:  "¡Perfil laboral! 👤\n\nPreguntas cortas, de a una.\n\n¿Nombre completo?",
    cognitiva:"¡Vamos a crear tu PERFIL! 👤\n\nPreguntas fáciles, una a la vez ✅\n\n¿Cuál es tu NOMBRE COMPLETO? ✍️",
  },
  cv: {
    ninguna: "¡Vamos a crear tu currículum vitae (CV)! 📄\n\nEl currículum vitae es tu puerta de entrada al trabajo. No importa si tienes poca experiencia — lo importante es presentarte bien.\n\n¿Cuál es tu nombre completo?",
    visual:  "¡Vamos a crear tu currículum vitae (CV) paso a paso! 📄\n\nLo construiremos sección por sección.\n\n¿Cuál es tu nombre completo?",
    auditiva:"¡Vamos a hacer tu currículum vitae (CV)! 📄\n\nTodo por texto, paso a paso ✅\n\n¿Cuál es tu nombre completo?",
    motora:  "¡Currículum vitae (CV)! 📄\n\nPaso a paso, preguntas cortas.\n\n¿Nombre completo?",
    cognitiva:"¡Vamos a hacer tu CURRÍCULUM! 📄\n\nEs un papel que muestra QUIÉN ERES ✅\n\nPaso a paso. ¡Tú puedes! 💪\n\n¿Cuál es tu NOMBRE COMPLETO? ✍️",
  },
  ofertas: {
    ninguna: "¡Aquí encontrarás empleos reales! 💼\n\nTrabajamos con portales especializados en inclusión laboral y empresas que valoran la diversidad.\n\n¿Qué tipo de trabajo te interesa? (por ejemplo: administrativo, producción, atención al cliente, otro)",
    visual:  "¡Empleos inclusivos! 💼\n\nTe daré descripciones detalladas de cómo acceder a cada portal de trabajo.\n\n¿Qué tipo de trabajo te interesa?",
    auditiva:"¡Empleos disponibles! 💼\n\nPortales de texto, sin necesidad de llamar ✅\n\n¿Qué tipo de trabajo buscas?",
    motora:  "¡Empleos! 💼\n\n¿Qué tipo de trabajo te interesa?\nOpción 1: Administrativo\nOpción 2: Bodega o producción\nOpción 3: Atención al cliente\nOpción 4: Otro",
    cognitiva:"¡Aquí hay TRABAJOS para ti! 💼 ✅\n\n¿Qué tipo de trabajo te GUSTA? ✍️",
  },
};

const getIntro = (mod, dis) => (INTROS[mod]||{})[dis] || (INTROS[mod]||{}).ninguna || "";

// ── Componente Mensaje ──────────────────────────────────────────────────────
const Msg = ({ msg, fontSize, hc }) => {
  const bot = msg.role === "bot";
  return (
    <div style={{ display:"flex", justifyContent:bot?"flex-start":"flex-end", marginBottom:14, padding:"0 10px" }}>
      {bot && (
        <div aria-hidden="true" style={{ width:36, height:36, borderRadius:"50%", background:S.purple, display:"flex", alignItems:"center", justifyContent:"center", fontSize:16, flexShrink:0, marginRight:8, alignSelf:"flex-end", boxShadow:"0 2px 6px rgba(83,56,140,0.3)" }}>
          🤝
        </div>
      )}
      <div role={bot?"article":undefined} style={{
        maxWidth:"78%", padding:"13px 17px",
        borderRadius: bot ? "4px 18px 18px 18px" : "18px 4px 18px 18px",
        background: hc ? (bot?"#1a0a33":"#003300") : (bot?S.white:"linear-gradient(135deg,"+S.purple+","+S.purpleDk+")"),
        color: hc ? "#FFFF00" : (bot?S.text:"#fff"),
        fontSize, lineHeight:1.65,
        boxShadow: hc ? "none" : (bot ? "0 2px 10px rgba(0,0,0,0.08)" : "0 3px 12px rgba(83,56,140,0.25)"),
        whiteSpace:"pre-wrap", wordBreak:"break-word",
        border: hc ? "2px solid #FFFF00" : (bot ? "1px solid #EDE8F7" : "none"),
      }}>
        {msg.loading ? (
          <span style={{ display:"inline-flex", gap:5, alignItems:"center" }}>
            <span style={{ fontSize:fontSize-1, opacity:0.7 }}>Escribiendo</span>
            {[0,1,2].map(i=>(
              <span key={i} style={{ width:6, height:6, borderRadius:"50%", background:S.purple, display:"inline-block", animation:`bounce 1s ease-in-out ${i*0.18}s infinite` }}/>
            ))}
          </span>
        ) : msg.content}
      </div>
    </div>
  );
};

// ── Secciones de términos (desplegables) ───────────────────────────────────
const TERMINOS = [
  {
    id:"quienes", titulo:"1. Quiénes somos",
    contenido: `Fundación SOFAN contribuye a la inclusión de personas con discapacidad en el mercado laboral. Apoyamos a las personas con discapacidad a ingresar al mercado de trabajo, a las empresas a cumplir con la Ley N° 20.422 y sus modificaciones (Ley de Inclusión), y contribuimos en la construcción de las mejores prácticas de inclusión laboral.\n\nNuestra misión es establecer con responsabilidad y seguridad la conexión entre organizaciones y personas con discapacidad. Creemos en el potencial de las personas con discapacidad y en el valor que la inclusión genera para todas las partes involucradas.`
  },
  {
    id:"uso", titulo:"2. Uso de la plataforma",
    contenido: `La Plataforma Laboral Inclusiva es operada por Servicios Audiovisuales SOFAN SpA (RUT 77.150.876-6) y Fundación de Beneficencia SOFAN SpA (RUT 65.206.325-K), ambas representadas por Rodrigo Antonio Moreno Moreno (RUN 15.878.659-1), domiciliadas en Angamos N° 374 C, Yungay, Ñuble.\n\nAl utilizar la plataforma, usted acepta cumplir estos términos en su totalidad. El uso es gratuito para las personas que buscan empleo.\n\nEl usuario se compromete a:\n• Utilizar la plataforma solo para los propósitos para los cuales fue diseñada.\n• Proporcionar información veraz y actualizada.\n• No transmitir contenidos falsos, difamatorios o que infrinjan derechos de terceros.\n• No causar daño técnico al sistema (virus, sobrecargas u otras acciones similares).\n• No intentar acceder a información de otros usuarios ni realizar ingeniería inversa del sistema.\n\nSOFAN se reserva el derecho de modificar estos términos en cualquier momento.`
  },
  {
    id:"responsabilidad", titulo:"3. Limitación de responsabilidad",
    contenido: `SOFAN actúa como plataforma de orientación e intermediación laboral. No tiene injerencia ni responsabilidad en los procesos de selección o contratación que realicen las empresas.\n\nSOFAN no valida ni garantiza la exactitud de las ofertas de empleo ni de la información proporcionada por los usuarios. Toda interacción entre partes se realiza bajo exclusiva responsabilidad de los propios usuarios.\n\nSOFAN implementa medidas de seguridad adecuadas; no obstante, no será responsable por accesos no autorizados o pérdidas de información provocadas por terceros a través de medios ilícitos, siempre que no medie dolo o culpa grave.`
  },
  {
    id:"datos", titulo:"4. Datos personales y privacidad",
    contenido: `Al utilizar esta plataforma, usted proporciona información personal voluntariamente, incluyendo datos relacionados con discapacidad, que son considerados datos sensibles según la Ley N° 19.628.\n\nSu información será utilizada para:\n• Adaptar la experiencia de orientación a sus necesidades específicas.\n• Conectarle con oportunidades de empleo compatibles con su perfil.\n• Elaborar estadísticas generales de uso (sin identificación personal).\n• Transferir sus datos a empresas aliadas o terceros (como la Bolsa Nacional de Empleo o ferias laborales), con el fin exclusivo de aumentar sus oportunidades de empleo.\n\nSOFAN no comparte sus datos personales con terceros sin su consentimiento, salvo por resolución judicial o acto administrativo que así lo ordene.\n\nUsted puede ejercer sus derechos de acceso, rectificación, cancelación u oposición, y revocar su consentimiento en cualquier momento, escribiendo a inclusion@sofan.cl.\n\nSOFAN emplea medidas técnicas y administrativas para proteger sus datos de accesos no autorizados.`
  },
  {
    id:"terminacion", titulo:"5. Suspensión del acceso",
    contenido: `SOFAN puede suspender o impedir el acceso a la plataforma si el usuario incumple estos términos y condiciones, o si se detectan irregularidades en la información proporcionada.`
  },
  {
    id:"contacto", titulo:"6. Contacto y legislación",
    contenido: `Para preguntas, reclamos o sugerencias sobre estos términos: inclusion@sofan.cl\n\nEstos términos se rigen e interpretan de acuerdo con las leyes de la República de Chile.`
  },
];

// ── Pantalla de bienvenida con términos integrados ─────────────────────────
const Welcome = ({ onSelect }) => {
  const [sel, setSel]         = useState(null);
  const [checked, setChecked] = useState(false);
  const [abierto, setAbierto] = useState(null);

  const handleSel = (id) => {
    setSel(id);
    setChecked(false);
  };

  const toggleSeccion = (id) => setAbierto(a => a === id ? null : id);

  return (
    <div style={{ minHeight:"100vh", background:`linear-gradient(160deg,${S.purpleDk} 0%,${S.purple} 55%,${S.magenta} 100%)`, display:"flex", alignItems:"center", justifyContent:"center", padding:20, fontFamily:"'Segoe UI','Helvetica Neue',sans-serif" }}>
      <div style={{ background:"rgba(255,255,255,0.98)", borderRadius:24, padding:"36px 28px", maxWidth:580, width:"100%", boxShadow:"0 24px 64px rgba(0,0,0,0.25)" }}>

        {/* Logo y título */}
        <div style={{ textAlign:"center", marginBottom:26 }}>
          <div style={{ display:"inline-flex", alignItems:"center", justifyContent:"center", width:64, height:64, borderRadius:"50%", background:`linear-gradient(135deg,${S.purple},${S.magenta})`, fontSize:28, marginBottom:12, boxShadow:"0 6px 20px rgba(83,56,140,0.35)" }}>🤝</div>
          <h1 style={{ fontSize:21, color:S.purpleDk, fontWeight:700, margin:"0 0 3px" }}>Plataforma Laboral Inclusiva</h1>
          <p style={{ color:S.purple, fontSize:12, fontWeight:600, margin:"0 0 6px", letterSpacing:"0.5px", textTransform:"uppercase" }}>Fundación SOFAN · Ñuble, Chile</p>
          <div style={{ height:3, background:S.yellow, borderRadius:2, maxWidth:100, margin:"8px auto 12px" }}/>
          <p style={{ color:S.muted, fontSize:13, lineHeight:1.65, margin:0 }}>
            Te ayudamos a encontrar trabajo.<br/>
            <strong style={{ color:S.text }}>¿Cómo podemos adaptar la experiencia para ti?</strong>
          </p>
        </div>

        {/* PASO 1 — Selección de discapacidad */}
        <fieldset style={{ border:"none", padding:0, margin:"0 0 20px" }}>
          <legend style={{ fontSize:11, fontWeight:700, color:S.muted, textTransform:"uppercase", letterSpacing:"0.8px", marginBottom:8, display:"block" }}>Paso 1 — Selecciona una opción</legend>
          <div style={{ display:"flex", flexDirection:"column", gap:7 }}>
            {DISABILITY_TYPES.map(d => (
              <button key={d.id} onClick={()=>handleSel(d.id)} aria-pressed={sel===d.id}
                style={{ display:"flex", alignItems:"center", gap:12, padding:"12px 14px", borderRadius:12, cursor:"pointer", textAlign:"left", transition:"all 0.18s",
                  border: sel===d.id ? `2.5px solid ${S.purple}` : `1.5px solid #DDD8F0`,
                  background: sel===d.id ? S.purpleL : "#FAFAF9",
                  boxShadow: sel===d.id ? `0 0 0 3px rgba(83,56,140,0.10)` : "none", outline:"none" }}>
                <div style={{ flex:1 }}>
                  <div style={{ fontWeight:700, color:S.text, fontSize:13 }}>{d.label}</div>
                  <div style={{ color:S.muted, fontSize:11, marginTop:1, lineHeight:1.4 }}>{d.desc}</div>
                </div>
                {sel===d.id && <span aria-hidden="true" style={{ color:S.purple, fontSize:17, fontWeight:700 }}>✓</span>}
              </button>
            ))}
          </div>
        </fieldset>

        {/* PASO 2 — Términos (solo aparece tras seleccionar) */}
        {sel && (
          <div style={{ borderTop:`2px solid ${S.purpleL}`, paddingTop:18, marginBottom:16 }}>
            <p style={{ fontSize:11, fontWeight:700, color:S.muted, textTransform:"uppercase", letterSpacing:"0.8px", margin:"0 0 10px" }}>
              Paso 2 — Términos de uso y privacidad
            </p>
            <p style={{ fontSize:12, color:S.muted, lineHeight:1.6, margin:"0 0 12px" }}>
              Antes de continuar, lee los términos que aplican a tu uso de esta plataforma. Puedes desplegar cada sección para leer su contenido.
            </p>

            {/* Secciones desplegables */}
            <div style={{ display:"flex", flexDirection:"column", gap:6, marginBottom:14 }}>
              {TERMINOS.map(t => (
                <div key={t.id} style={{ border:`1px solid ${abierto===t.id ? S.purple : "#DDD8F0"}`, borderRadius:10, overflow:"hidden", transition:"border-color 0.18s" }}>
                  <button onClick={()=>toggleSeccion(t.id)}
                    aria-expanded={abierto===t.id}
                    aria-controls={`terms-${t.id}`}
                    style={{ width:"100%", display:"flex", alignItems:"center", justifyContent:"space-between", padding:"10px 14px", background: abierto===t.id ? S.purpleL : "#FAFAF9", border:"none", cursor:"pointer", textAlign:"left", gap:8 }}>
                    <span style={{ fontSize:12, fontWeight:700, color: abierto===t.id ? S.purpleDk : S.text }}>{t.titulo}</span>
                    <span aria-hidden="true" style={{ fontSize:14, color:S.purple, flexShrink:0, transform: abierto===t.id ? "rotate(180deg)" : "none", transition:"transform 0.2s" }}>▾</span>
                  </button>
                  {abierto===t.id && (
                    <div id={`terms-${t.id}`} role="region" style={{ padding:"12px 14px", background:S.white, borderTop:`1px solid ${S.purpleL}` }}>
                      {t.contenido.split("\n").map((p,i) => p.trim() === "" ? null : (
                        <p key={i} style={{ fontSize:11, color:"#3A2560", lineHeight:1.75, margin:"0 0 8px" }}>{p}</p>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Checkbox de aceptación */}
            <label style={{ display:"flex", alignItems:"flex-start", gap:10, cursor:"pointer", padding:"12px 14px", background:S.purpleL, borderRadius:10, border:`1.5px solid ${S.purple}30` }}>
              <input type="checkbox" checked={checked} onChange={e=>setChecked(e.target.checked)}
                style={{ marginTop:2, accentColor:S.purple, width:16, height:16, flexShrink:0, cursor:"pointer" }}
                aria-label="Declaro haber leído y acepto los Términos de Uso y Política de Privacidad de la Plataforma Laboral Inclusiva de Fundación SOFAN"/>
              <span style={{ fontSize:12, color:S.purpleDk, lineHeight:1.55 }}>
                Declaro haber leído y acepto los <strong>Términos de Uso y Política de Privacidad</strong> de la Plataforma Laboral Inclusiva de Fundación SOFAN, y autorizo el tratamiento de mis datos personales, incluyendo datos sensibles relacionados con discapacidad, conforme a lo descrito.
              </span>
            </label>
          </div>
        )}

        {/* Botón de inicio */}
        <button onClick={()=>sel&&checked&&onSelect(sel)} disabled={!sel||!checked} aria-disabled={!sel||!checked}
          style={{ width:"100%", padding:"16px 0", borderRadius:14, border:"none",
            background: sel&&checked ? `linear-gradient(135deg,${S.purple},${S.magenta})` : "#D5D0E8",
            color: sel&&checked ? "#fff" : "#AAA", fontSize:15, fontWeight:700,
            cursor: sel&&checked ? "pointer" : "not-allowed",
            transition:"all 0.2s", boxShadow: sel&&checked ? "0 6px 20px rgba(83,56,140,0.35)" : "none" }}>
          {!sel ? "Elige una opción para continuar" : !checked ? "Acepta los términos para continuar" : "¡Comenzar! →"}
        </button>

        {/* Badges */}
        <div style={{ display:"flex", gap:6, flexWrap:"wrap", justifyContent:"center", marginTop:16 }}>
          {["WCAG 2.1 AAA","Convención ONU 2006","Ley 21.015"].map(b=>(
            <span key={b} style={{ fontSize:10, fontWeight:700, color:S.purple, background:S.purpleL, padding:"3px 9px", borderRadius:20, border:`1px solid ${S.purple}30` }}>{b}</span>
          ))}
        </div>
        <p style={{ textAlign:"center", color:"#C0BAD8", fontSize:11, marginTop:10 }}>
          Esta selección solo personaliza tu experiencia. No es obligatorio compartirla.
        </p>
      </div>
    </div>
  );
};

// ── App principal ───────────────────────────────────────────────────────────
export default function ChatbotSOFAN() {
  const [screen, setScreen]         = useState("welcome");
  const [disability, setDisability] = useState(null);
  const [activeModule, setActive]   = useState("orientacion");
  const [convs, setConvs]           = useState({ orientacion:[], perfil:[], cv:[], ofertas:[] });
  const [input, setInput]           = useState("");
  const [loading, setLoading]       = useState(false);
  const [fontSize, setFontSize]     = useState(15);
  const [hc, setHc]                 = useState(false);
  const [showA11y, setShowA11y]     = useState(false);

  // MEJORA 1: Estado del perfil laboral completado
  const [perfilData, setPerfilData] = useState(null);

  const endRef   = useRef(null);
  const inputRef = useRef(null);
  const msgs     = convs[activeModule];
  const mod      = MODULES.find(m=>m.id===activeModule);

  useEffect(()=>{ endRef.current?.scrollIntoView({behavior:"smooth"}); }, [convs, activeModule]);

  const handleStart = (d) => {
    setDisability(d);
    if (d==="visual")    setFontSize(18);
    if (d==="cognitiva") setFontSize(17);
    const intro = getIntro("orientacion", d);
    setConvs(p=>({ ...p, orientacion:[{role:"bot",content:intro}] }));
    setScreen("chat");
  };

  const switchModule = (id) => {
    setActive(id);
    if (convs[id].length === 0) {
      let intro = getIntro(id, disability||"ninguna");
      // MEJORA 1: Si hay perfil completado y van a CV, avisar que se usará
      if (id === "cv" && perfilData) {
        intro = `¡Perfecto! 📄 Ya tengo tu perfil laboral guardado.\n\nUsaré la información que ya me diste para crear tu currículum vitae (CV) sin que tengas que repetirla. Solo te pediré los datos que faltan.\n\n¿Quieres comenzar?`;
      }
      setConvs(p=>({ ...p, [id]:[{role:"bot",content:intro}] }));
    }
  };

  // MEJORA 1: Detectar si el perfil fue completado analizando la conversación
  const detectarPerfil = (msgs) => {
    const texto = msgs.map(m=>m.content).join("\n").toLowerCase();
    if (texto.includes("resumen") && texto.includes("perfil") && texto.includes("nombre")) {
      // Extraer el resumen del perfil del último mensaje del bot que lo mencione
      const resumenMsg = [...msgs].reverse().find(m=>m.role==="bot" && m.content.toLowerCase().includes("nombre") && m.content.length > 200);
      if (resumenMsg) return resumenMsg.content;
    }
    return null;
  };

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;
    const userMsg = {role:"user",content:text};
    const spinner = {role:"bot",content:"",loading:true};
    setConvs(p=>({ ...p, [activeModule]:[...p[activeModule],userMsg,spinner] }));
    setInput("");
    setLoading(true);

    try {
      const history = [...msgs, userMsg].filter(m=>!m.loading).map(m=>({ role:m.role==="bot"?"assistant":"user", content:m.content }));

      // MEJORA 1: pasar contexto del perfil al módulo CV
      const extraCtx = (activeModule === "cv" && perfilData) ? perfilData : "";
      const system   = BASE_PROMPT(activeModule, extraCtx) + (DISABILITY_CTX[disability||"ninguna"]||"");

      const res  = await fetch("https://api.anthropic.com/v1/messages",{
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({ model:"claude-sonnet-4-20250514", max_tokens:1000, system, messages:history })
      });
      const data = await res.json();
      const bot  = data.content?.[0]?.text || "Lo siento, hubo un error. Por favor intenta de nuevo.";

      setConvs(p=>{
        const updated = [...p[activeModule].filter(m=>!m.loading), {role:"bot",content:bot}];
        // MEJORA 1: detectar si el perfil se completó para guardarlo
        if (activeModule === "perfil" && !perfilData) {
          const detectado = detectarPerfil(updated);
          if (detectado) setPerfilData(detectado);
        }
        return { ...p, [activeModule]:updated };
      });
    } catch {
      setConvs(p=>({ ...p, [activeModule]:[...p[activeModule].filter(m=>!m.loading),{role:"bot",content:"⚠️ Error de conexión. Por favor intenta de nuevo."}] }));
    }
    setLoading(false);
  };

  const a11yBtn = {
    padding:"6px 14px", borderRadius:8,
    border:`1.5px solid ${hc?"#FFFF00":"#C8C0E0"}`,
    background:hc?"#222":"#F4F1FA",
    color:hc?"#FFFF00":S.purple, cursor:"pointer",
    fontSize:12, fontWeight:700
  };

  if (screen==="welcome") return <Welcome onSelect={handleStart}/>;

  const qr = QUICK_REPLIES[activeModule]||[];

  return (
    <div style={{ height:"100vh", display:"flex", flexDirection:"column", background:hc?"#000":S.bg, fontFamily:"'Segoe UI','Helvetica Neue',sans-serif", fontSize, color:hc?"#FFFF00":S.text }} role="application" aria-label="Plataforma Laboral Inclusiva SOFAN">

      <style>{`
        @keyframes bounce{0%,80%,100%{transform:translateY(0);opacity:.4}40%{transform:translateY(-7px);opacity:1}}
        ::-webkit-scrollbar{width:5px}
        ::-webkit-scrollbar-thumb{background:${S.purple}40;border-radius:3px}
        button:focus-visible{outline:3px solid ${S.yellow};outline-offset:2px}
        input:focus,textarea:focus{outline:3px solid ${S.purple}60;outline-offset:0}
      `}</style>

      {/* HEADER */}
      <header style={{ background:hc?"#000":`linear-gradient(135deg,${mod.color},${S.purpleDk})`, color:"#fff", padding:"11px 16px", display:"flex", alignItems:"center", gap:12, flexShrink:0, boxShadow:"0 2px 12px rgba(0,0,0,0.2)" }}>
        <span aria-hidden="true" style={{ fontSize:22 }}>{mod.icon}</span>
        <div style={{ flex:1 }}>
          <div style={{ fontWeight:700, fontSize:fontSize+1, lineHeight:1.2 }}>{mod.label}</div>
          <div style={{ fontSize:fontSize-3, opacity:0.85 }}>Fundación SOFAN · Plataforma Laboral Inclusiva</div>
        </div>
        {/* Badge perfil completado */}
        {perfilData && (
          <div title="Perfil laboral completado" style={{ background:S.yellow, color:S.purpleDk, fontSize:10, fontWeight:800, padding:"3px 8px", borderRadius:10 }}>✓ Perfil</div>
        )}
        <button onClick={()=>setShowA11y(!showA11y)} aria-expanded={showA11y} aria-controls="panel-a11y" aria-label="Opciones de accesibilidad"
          style={{ background:"rgba(255,255,255,0.18)", border:"1.5px solid rgba(255,255,255,0.4)", borderRadius:8, padding:"7px 10px", color:"#fff", cursor:"pointer", fontSize:16 }}>
          ♿
        </button>
      </header>

      {/* PANEL A11Y */}
      {showA11y && (
        <div id="panel-a11y" role="region" aria-label="Opciones de accesibilidad" style={{ background:hc?"#111":S.white, borderBottom:`2px solid ${hc?"#FFFF00":"#DDD8F0"}`, padding:"12px 16px", display:"flex", gap:10, flexWrap:"wrap", alignItems:"center", flexShrink:0 }}>
          <span style={{ fontWeight:700, fontSize:fontSize-1, color:hc?"#FFFF00":S.purple }}>♿ Accesibilidad:</span>
          <div style={{ display:"flex", gap:6, alignItems:"center" }}>
            <label style={{ fontSize:12, color:hc?"#FFFF00":S.muted }}>Tamaño de texto:</label>
            <button onClick={()=>setFontSize(f=>Math.max(12,f-2))} style={a11yBtn} aria-label="Reducir tamaño de texto">A−</button>
            <button onClick={()=>setFontSize(f=>Math.min(24,f+2))} style={a11yBtn} aria-label="Aumentar tamaño de texto">A+</button>
          </div>
          <button onClick={()=>setHc(!hc)} style={{ ...a11yBtn, background:hc?"#FFFF00":S.purpleDk, color:hc?"#000":"#fff" }} aria-pressed={hc}>
            {hc?"☀️ Modo normal":"🌑 Alto contraste"}
          </button>
          <span style={{ fontSize:11, color:hc?"#FFFF00":"#B0A8CC" }}>
            Perfil: {DISABILITY_TYPES.find(d=>d.id===disability)?.label}
          </span>
        </div>
      )}

      {/* TABS de módulos */}
      <nav aria-label="Módulos disponibles" style={{ display:"flex", background:hc?"#111":S.white, borderBottom:`1px solid ${hc?"#FFFF00":"#E8E4F5"}`, overflowX:"auto", flexShrink:0 }}>
        {MODULES.map(m=>{
          const active = activeModule===m.id;
          return (
            <button key={m.id} onClick={()=>switchModule(m.id)} aria-current={active?"page":undefined}
              style={{ flex:1, minWidth:72, padding:"10px 6px 8px", border:"none", borderBottom:active?`3px solid ${m.color}`:"3px solid transparent",
                background:active?(hc?"#222":`${m.color}12`):"transparent",
                color:hc?"#FFFF00":(active?m.color:"#8C83AA"), cursor:"pointer",
                fontSize:fontSize-3, fontWeight:active?700:400,
                display:"flex", flexDirection:"column", alignItems:"center", gap:3, transition:"all 0.18s" }}>
              <span aria-hidden="true" style={{ fontSize:17 }}>{m.icon}</span>
              <span style={{ lineHeight:1.2, textAlign:"center" }}>{m.label}</span>
              {m.id==="cv" && perfilData && <span aria-hidden="true" style={{ fontSize:9, color:S.yellow, fontWeight:800 }}>✓ datos</span>}
            </button>
          );
        })}
      </nav>

      {/* MENSAJES */}
      <main style={{ flex:1, overflowY:"auto", padding:"16px 4px", background:hc?"#000":S.bg }} role="log" aria-live="polite" aria-label="Mensajes del chat" aria-atomic="false">
        {msgs.map((msg,i)=><Msg key={i} msg={msg} fontSize={fontSize} hc={hc}/>)}
        <div ref={endRef}/>
      </main>

      {/* RESPUESTAS RÁPIDAS */}
      {qr.length>0 && msgs.length<=2 && (
        <div role="group" aria-label="Sugerencias de preguntas" style={{ padding:"8px 12px", background:hc?"#111":S.white, borderTop:`1px solid ${hc?"#FFFF00":"#E8E4F5"}`, display:"flex", gap:8, overflowX:"auto", flexShrink:0 }}>
          {qr.map((q,i)=>(
            <button key={i} onClick={()=>{ setInput(q); inputRef.current?.focus(); }}
              style={{ whiteSpace:"nowrap", padding:"8px 14px", borderRadius:20,
                border:`1.5px solid ${hc?"#FFFF00":mod.color}`,
                background:hc?"#000":`${mod.color}10`,
                color:hc?"#FFFF00":mod.color,
                cursor:"pointer", fontSize:fontSize-2, flexShrink:0, fontWeight:500,
                transition:"all 0.15s" }}>
              {q}
            </button>
          ))}
        </div>
      )}

      {/* INPUT */}
      <footer style={{ padding:"12px 14px", background:hc?"#111":S.white, borderTop:`2px solid ${hc?"#FFFF00":"#E8E4F5"}`, display:"flex", gap:10, alignItems:"flex-end", flexShrink:0 }}>
        <textarea ref={inputRef} value={input} onChange={e=>setInput(e.target.value)}
          onKeyDown={e=>{ if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();send();} }}
          placeholder="Escribe tu mensaje aquí..." aria-label="Campo de texto para escribir tu mensaje" rows={1}
          style={{ flex:1, padding:"12px 16px", borderRadius:22, border:`2px solid ${hc?"#FFFF00":"#DDD8F0"}`,
            fontSize, resize:"none", background:hc?"#000":S.bg, color:hc?"#FFFF00":S.text,
            outline:"none", lineHeight:1.45, maxHeight:100, overflowY:"auto", fontFamily:"inherit",
            transition:"border-color 0.15s" }}/>
        <button onClick={send} disabled={loading||!input.trim()} aria-label={loading?"Enviando mensaje...":"Enviar mensaje"}
          style={{ width:48, height:48, borderRadius:"50%", border:"none",
            background: loading||!input.trim() ? "#C8C0E0" : `linear-gradient(135deg,${S.purple},${S.magenta})`,
            color:"#fff", fontSize:18, cursor:loading||!input.trim()?"not-allowed":"pointer",
            display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0,
            transition:"all 0.2s", boxShadow:loading||!input.trim()?"none":"0 4px 14px rgba(83,56,140,0.4)" }}>
          {loading ? "⏳" : "➤"}
        </button>
      </footer>
    </div>
  );
}
