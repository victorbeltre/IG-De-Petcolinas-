"""
Plan de Campana de Marketing Anual — PetColinas
Calendario editorial, temas mensuales, fechas clave y campanas promocionales.

Uso: importar get_campaign_context(date) para obtener el contexto
de campana del dia y pasarlo al generador de contenido.
"""

import datetime
from typing import Optional

# ---------------------------------------------------------------------------
# Temas mensuales
# ---------------------------------------------------------------------------

MONTHLY_THEMES = {
    1:  {
        "nombre": "Año Nuevo, Rutina Nueva",
        "descripcion": "Inicio del año: nuevos hábitos de cuidado, chequeo veterinario y renovación de membresías.",
        "servicio_estrella": "membresia",
        "promo": "10% OFF en membresías nuevas durante enero",
        "cta": "Empieza el año con el plan que tu peludito merece.",
    },
    2:  {
        "nombre": "Amor Peludo",
        "descripcion": "San Valentín: celebrar el amor incondicional de las mascotas. Baños especiales y paquetes de grooming.",
        "servicio_estrella": "grooming",
        "promo": "Baño + lazo o pañuelo de regalo en San Valentín",
        "cta": "Dales el mejor regalo: llévalo recién bañado este 14 de febrero.",
    },
    3:  {
        "nombre": "Primavera Peludita",
        "descripcion": "Temporada de muda de pelo: grooming profundo, deslanado y cuidado de piel.",
        "servicio_estrella": "grooming",
        "promo": "Baño medicado con descuento para pieles sensibles",
        "cta": "La muda de pelo no tiene que ser un problema. Nosotros te ayudamos.",
    },
    4:  {
        "nombre": "Salud Total",
        "descripcion": "Mes de la salud animal: vacunas al día, desparasitación y chequeos preventivos.",
        "servicio_estrella": "veterinaria",
        "promo": "Consulta + vacuna quíntuple por precio especial",
        "cta": "Prevenir es más barato que curar. Agenda la consulta hoy.",
    },
    5:  {
        "nombre": "Mamá y su Peludo",
        "descripcion": "Día de las Madres: reconocer a las mamás peludistas. Grooming especial de regalo.",
        "servicio_estrella": "grooming",
        "promo": "Certificado de regalo para el peludito de mamá",
        "cta": "¿Qué mejor regalo para mamá que llevar su peludo impecable?",
    },
    6:  {
        "nombre": "Verano Fresco",
        "descripcion": "Calor dominicano al máximo: baños frecuentes, cortes de verano y hidratación del pelaje.",
        "servicio_estrella": "grooming",
        "promo": "2do baño al 50% OFF en junio con membresía Básica",
        "cta": "El calor no perdona. Mantenlo fresco y feliz todo el mes.",
    },
    7:  {
        "nombre": "Hidratación y Frescura",
        "descripcion": "Julio de calor: tratamientos hidratantes, baños con línea premium y rutina de verano.",
        "servicio_estrella": "grooming",
        "promo": "Baño con línea hidratante incluido en membresía Plus",
        "cta": "Un pelaje hidratado es un perro feliz en pleno verano.",
    },
    8:  {
        "nombre": "Mes del Perro",
        "descripcion": "Agosto 26 = Día Mundial del Perro. Mes entero de celebración, fotos y premios.",
        "servicio_estrella": "grooming",
        "promo": "Foto profesional gratis con cada grooming completo en agosto",
        "cta": "Este mes celebramos a todos nuestros peluditos. ¡Trae al tuyo!",
    },
    9:  {
        "nombre": "Regreso a la Rutina",
        "descripcion": "Post-verano: retomar la rutina de grooming y veterinaria después de las vacaciones.",
        "servicio_estrella": "membresia",
        "promo": "Membresía Plus sin costo de inscripción en septiembre",
        "cta": "Las vacaciones terminaron. La rutina de cuidado empieza hoy.",
    },
    10: {
        "nombre": "Halloween Peludito",
        "descripcion": "Octubre de disfraces y sesiones de fotos. Grooming temático y concurso de disfraces.",
        "servicio_estrella": "grooming",
        "promo": "Grooming con disfraz de Halloween gratis para los primeros 10",
        "cta": "¿Tu peludito ya tiene disfraz? Nosotros lo ponemos lindo primero.",
    },
    11: {
        "nombre": "Gratitud Peluda",
        "descripcion": "Mes de gratitud: campana de membresías, testimonios de clientes y contenido emocional.",
        "servicio_estrella": "membresia",
        "promo": "Regala una membresía Básica este mes de Acción de Gracias",
        "cta": "Agradece con el mejor cuidado. Membresías disponibles todo noviembre.",
    },
    12: {
        "nombre": "Navidad Peludita",
        "descripcion": "Diciembre festivo: grooming navideño, sesiones de fotos con Santa y cierre del año.",
        "servicio_estrella": "grooming",
        "promo": "Grooming completo navideño + foto con Santa Claus",
        "cta": "¡Que tu peludito llegue impecable a la Nochebuena!",
    },
}

# ---------------------------------------------------------------------------
# Fechas especiales
# ---------------------------------------------------------------------------

SPECIAL_DATES = {
    # Fechas fijas
    (1, 1):   {"evento": "Año Nuevo", "tipo": "festivo", "tono": "celebracion",
               "idea": "Post de inicio de año con propósitos de cuidado para tu mascota."},
    (1, 21):  {"evento": "Día de la Altagracia", "tipo": "feriado_rd", "tono": "emocional",
               "idea": "Post de fe y amor: así como cuidas tu hogar, cuida a tu peludito."},
    (2, 14):  {"evento": "San Valentín", "tipo": "comercial", "tono": "romantico",
               "idea": "El amor incondicional de tu mascota. Promo de baño especial."},
    (2, 20):  {"evento": "Día Mundial del Gato", "tipo": "mundial_animal", "tono": "educativo",
               "idea": "Aunque somos dog-friendly, celebramos a todos los peluditos."},
    (2, 27):  {"evento": "Día de la Independencia Dominicana", "tipo": "feriado_rd", "tono": "patriotico",
               "idea": "Celebra con tu mascota. Colores patrios + peludito arreglado."},
    (4, 22):  {"evento": "Día de la Tierra", "tipo": "mundial", "tono": "educativo",
               "idea": "Productos eco-friendly, cuidado responsable del medio ambiente."},
    (5, 1):   {"evento": "Día del Trabajador", "tipo": "feriado_rd", "tono": "relajado",
               "idea": "Día libre con tu peludito. ¡Aprovecha y tráelo a grooming!"},
    (6, 1):   {"evento": "Día Mundial del Perro sin Hogar", "tipo": "mundial_animal", "tono": "concientizacion",
               "idea": "Post de adopción responsable y cuidado de animales."},
    (8, 16):  {"evento": "Día de la Restauración", "tipo": "feriado_rd", "tono": "patriotico",
               "idea": "Feriado patrio con tu peludito. Promo especial de grooming."},
    (8, 26):  {"evento": "Día Mundial del Perro", "tipo": "mundial_animal", "tono": "celebracion",
               "idea": "El día más importante del año para PetColinas. Celebración total."},
    (10, 4):  {"evento": "Día Mundial de los Animales", "tipo": "mundial_animal", "tono": "educativo",
               "idea": "Reflexión sobre el amor y cuidado responsable de mascotas."},
    (10, 29): {"evento": "Día Mundial del Veterinario", "tipo": "mundial_animal", "tono": "reconocimiento",
               "idea": "Reconocer al equipo veterinario de PetColinas. Post de confianza."},
    (10, 31): {"evento": "Halloween", "tipo": "comercial", "tono": "divertido",
               "idea": "Concurso de disfraces peludos. Grooming temático de Halloween."},
    (12, 24): {"evento": "Nochebuena", "tipo": "festivo", "tono": "calido",
               "idea": "Tu peludito listo para la cena de Nochebuena. Grooming especial."},
    (12, 25): {"evento": "Navidad", "tipo": "festivo", "tono": "calido",
               "idea": "Feliz Navidad de PetColinas. Post emotivo con los clientes del año."},
    (12, 31): {"evento": "Fin de Año", "tipo": "festivo", "tono": "reflexivo",
               "idea": "Resumen del año en fotos. Gracias a todos los peluditos de PetColinas."},
}

# Fechas variables (se recalculan por año)
def _last_sunday_of_may(year: int) -> datetime.date:
    """Día de las Madres en República Dominicana: último domingo de mayo."""
    d = datetime.date(year, 5, 31)
    while d.weekday() != 6:
        d -= datetime.timedelta(days=1)
    return d

def _get_variable_dates(year: int) -> dict:
    return {
        _last_sunday_of_may(year): {
            "evento": "Día de las Madres (RD)",
            "tipo": "comercial",
            "tono": "emocional",
            "idea": "El peludito de mamá merece lucir espectacular. Promo de grooming.",
        },
    }

# ---------------------------------------------------------------------------
# Campanas trimestrales
# ---------------------------------------------------------------------------

QUARTERLY_CAMPAIGNS = {
    "Q1": {
        "meses": [1, 2, 3],
        "nombre": "Nuevo Año, Nuevo Peludo",
        "objetivo": "Captación de nuevas membresías y chequeos de inicio de año",
        "kpi": "Membresías nuevas, consultas veterinarias",
        "mensaje_central": "Empieza el año con el mejor cuidado para tu mascota.",
        "acciones": [
            "Promo de membresía con descuento de inscripción",
            "Pack de bienvenida para nuevos clientes",
            "Contenido educativo: guía de cuidados del año",
        ],
    },
    "Q2": {
        "meses": [4, 5, 6],
        "nombre": "Temporada de Calor",
        "objetivo": "Aumentar frecuencia de baños y visitas veterinarias preventivas",
        "kpi": "Servicios de grooming, vacunaciones",
        "mensaje_central": "El calor dominicano exige cuidado extra. Nosotros estamos aquí.",
        "acciones": [
            "Campaña de vacunación preventiva",
            "Promo de baños para temporada de calor",
            "Contenido: signos de golpe de calor en mascotas",
        ],
    },
    "Q3": {
        "meses": [7, 8, 9],
        "nombre": "Verano Peludito",
        "objetivo": "Retención de clientes activos y celebración del Día Mundial del Perro",
        "kpi": "Frecuencia de visitas, engagement en Instagram",
        "mensaje_central": "El verano es nuestro momento. Tu peludo merece lo mejor.",
        "acciones": [
            "Concurso de fotos en Instagram (agosto 26)",
            "Baños especiales de verano",
            "Spotlight de clientes: fotos antes y después",
        ],
    },
    "Q4": {
        "meses": [10, 11, 12],
        "nombre": "Fiesta Peludita",
        "objetivo": "Grooming de temporada festiva y campana de membresías como regalo",
        "kpi": "Grooming navideño, membresías regaladas",
        "mensaje_central": "La época más linda del año. Tu peludo tiene que lucir espectacular.",
        "acciones": [
            "Grooming Halloween temático",
            "Membresías como regalo de Navidad",
            "Sesiones de fotos navideñas con Santa",
            "Resumen del año en Instagram Stories",
        ],
    },
}

# ---------------------------------------------------------------------------
# Pilares de contenido y frecuencia recomendada
# ---------------------------------------------------------------------------

CONTENT_PILLARS = {
    "grooming": {
        "frecuencia_semanal": 3,
        "descripcion": "Antes/después, tips de cuidado en casa, técnicas de grooming",
        "formatos": ["foto_perro", "antes_despues", "educativo"],
    },
    "veterinaria": {
        "frecuencia_semanal": 1,
        "descripcion": "Salud preventiva, vacunas, consultas, tips de bienestar",
        "formatos": ["educativo", "urgencia"],
    },
    "membresia": {
        "frecuencia_semanal": 1,
        "descripcion": "Beneficios, testimonios, comparativa de planes",
        "formatos": ["membresia"],
    },
    "comunidad": {
        "frecuencia_semanal": 2,
        "descripcion": "Clientes satisfechos, testimonios, memes dominicanos de mascotas",
        "formatos": ["antes_despues", "educativo"],
    },
}

# ---------------------------------------------------------------------------
# Funcion principal: obtener contexto de campana para una fecha
# ---------------------------------------------------------------------------

def get_campaign_context(date: Optional[datetime.date] = None) -> dict:
    """
    Retorna el contexto completo de campana para la fecha dada.
    Incluye tema mensual, campana trimestral y evento especial (si aplica).
    """
    if date is None:
        date = datetime.date.today()

    month = date.month
    quarter = (month - 1) // 3 + 1
    quarter_key = f"Q{quarter}"

    monthly = MONTHLY_THEMES[month]
    quarterly = QUARTERLY_CAMPAIGNS[quarter_key]

    # Verificar fechas especiales fijas
    special = SPECIAL_DATES.get((date.month, date.day))

    # Verificar fechas variables
    if special is None:
        variable_dates = _get_variable_dates(date.year)
        special = variable_dates.get(date)

    context = {
        "fecha": date.isoformat(),
        "mes": month,
        "trimestre": quarter_key,
        "tema_mensual": monthly,
        "campana_trimestral": quarterly,
        "evento_especial": special,
        "es_fecha_especial": special is not None,
    }

    return context


def format_campaign_context_for_prompt(date: Optional[datetime.date] = None) -> str:
    """
    Formatea el contexto de campana como texto para incluir en el prompt de Claude.
    """
    ctx = get_campaign_context(date)
    monthly = ctx["tema_mensual"]
    quarterly = ctx["campana_trimestral"]

    lines = [
        "=== CONTEXTO DE CAMPANA DE MARKETING ===",
        f"Trimestre: {ctx['trimestre']} — {quarterly['nombre']}",
        f"Objetivo trimestral: {quarterly['objetivo']}",
        f"Mensaje central del trimestre: {quarterly['mensaje_central']}",
        "",
        f"Tema del mes: {monthly['nombre']}",
        f"Descripcion: {monthly['descripcion']}",
        f"Servicio estrella este mes: {monthly['servicio_estrella'].upper()}",
        f"Promocion activa: {monthly['promo']}",
        f"CTA sugerido: {monthly['cta']}",
    ]

    if ctx["es_fecha_especial"]:
        ev = ctx["evento_especial"]
        lines += [
            "",
            f"FECHA ESPECIAL HOY: {ev['evento']}",
            f"Tono recomendado: {ev['tono']}",
            f"Idea de contenido: {ev['idea']}",
            "INSTRUCCION: Incorpora este evento especial en el post de hoy.",
        ]

    lines.append("=== FIN CONTEXTO DE CAMPANA ===")
    return "\n".join(lines)


if __name__ == "__main__":
    import json
    ctx = get_campaign_context()
    print(json.dumps(ctx, ensure_ascii=False, indent=2, default=str))
    print()
    print(format_campaign_context_for_prompt())
