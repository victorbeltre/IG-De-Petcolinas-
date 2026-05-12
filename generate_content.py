"""
Orquestador automatico de contenido para PetColinas.
Integra la formula Portrait de claude-banana para prompts de imagen de alta calidad.

Genera dos archivos en el directorio actual:
  post_del_dia.jpg  -> imagen 1080x1080 JPEG con logo de PetColinas
  caption.txt       -> caption listo para Instagram

Variable de entorno requerida:
  ANTHROPIC_API_KEY  -> API key de Claude (Anthropic)

Opcional:
  HORDE_KEY  -> API key de Stable Horde (gratis en stablehorde.net)
               Si no se define, usa clave anonima (mas lenta pero funciona)
"""

import os
import json
import re
import time
import base64
import datetime
from io import BytesIO
from pathlib import Path

import anthropic
import requests
from PIL import Image

from campaign_plan import format_campaign_context_for_prompt, get_campaign_context
from content_log import format_history_for_prompt, suggest_content_type, append_post, get_recent_breeds

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

COMPETITOR_INSIGHTS_FILE = "competitor_insights.json"


def _load_competitor_insights() -> str:
    """Carga el ultimo reporte de inteligencia competitiva si existe y es reciente (< 30 dias)."""
    path = Path(COMPETITOR_INSIGHTS_FILE)
    if not path.exists():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        fecha = data.get("fecha_analisis", "")
        if fecha:
            age = (datetime.date.today() - datetime.date.fromisoformat(fecha)).days
            if age > 30:
                return ""
        opps = data.get("oportunidades_diferenciacion", [])
        recs = data.get("recomendaciones_contenido", [])
        lines = ["=== INTELIGENCIA COMPETITIVA (usar para diferenciarse) ==="]
        if opps:
            lines.append("Oportunidades detectadas vs competencia:")
            for o in opps[:3]:
                lines.append(f"  - {o.get('oportunidad', '')}: {o.get('estrategia', '')}")
        if recs:
            lines.append("Ideas de contenido diferenciador:")
            for r in recs[:3]:
                lines.append(f"  - [{r.get('tipo', '')}] {r.get('tema', '')}: {r.get('caption_idea', '')[:80]}")
        lines.append("=== FIN INTELIGENCIA COMPETITIVA ===")
        return "\n".join(lines)
    except Exception:
        return ""

# Stable Horde — red comunitaria de GPUs, 100% gratuita
# Clave anonima "0000000000" funciona sin registro (menor prioridad en cola)
HORDE_API = "https://stablehorde.net/api/v2"
HORDE_MODELS = ["Realistic Vision V6.0 B1", "Deliberate", "Dreamshaper"]

# ---------------------------------------------------------------------------
# Contexto de marca
# ---------------------------------------------------------------------------

PETCOLINAS = """
EMPRESA: PetColinas — Veterinaria y Peluqueria Canina
UBICACION: Plaza Las Colinas, Av. Prolongacion 27 de Febrero, Santo Domingo Oeste, RD
WHATSAPP: 809-752-6806 | INSTAGRAM: @petcolinas
HORARIO: Todos los dias EXCEPTO martes

SERVICIOS Y PRECIOS:
  Grooming -> Bano cachorro RD$699 | pequeno RD$799 | mediano RD$949 | grande RD$1,149
              Corte higienico RD$490 | completo RD$749 | bano medicado RD$950
              Bano pequeno con linea RD$999
  Veterinaria -> Consulta RD$1,500 | Vacuna quintuple RD$1,200 | Rabia RD$1,500
                 Giardia RD$1,450 | Bordetella RD$1,400 | Albendazol RD$300
  Membresias -> Basica RD$2,800/mes: 4 banos + turno prioritario + 10% OFF farmacia
                Plus RD$4,200/mes: 4 banos + 1 corte + turno VIP + 15% OFF + consulta gratis

COLORES DE MARCA: Verde oscuro #1a6b3a | Naranja #d45f1e | Dorado #c9a227

ESTILO: Calido, dominicano, cercano. Frases como "peludito", "nube de algodon",
  "bajo a perro", "tu peludo merece lo mejor". Nunca corporativo ni frio.

HASHTAGS: #PetColinas #GroomingRD #VeterinariaRD #MascotasRD #PerrosRD
          #SantoDomingoOeste #BanoPerros #PeluqueriaCanina #MascotasFelices #CuidaTuMascota
"""

CONTENT_TYPES = ["grooming", "veterinaria", "membresia", "educativo", "urgencia", "antes_despues"]

DOG_BREEDS = [
    "Golden Retriever", "Labrador Retriever", "Poodle", "Shih Tzu",
    "Maltese", "French Bulldog", "Bichon Frise", "Cocker Spaniel",
    "Schnauzer", "Yorkshire Terrier", "Havanese", "Pomeranian",
]

# ---------------------------------------------------------------------------
# Formula Portrait de claude-banana (7 componentes, modo retrato)
# ---------------------------------------------------------------------------

PORTRAIT_FORMULA = """
=== FORMULA DE IMAGEN — PORTRAIT MODE (claude-banana) ===

Distribucion de componentes para fotografia de mascotas:
  1. Sujeto      30% — raza, edad, color de pelaje, expresion, rasgos unicos
  2. Estilo      20% — fotografia editorial documental, referencia de publicacion
  3. Iluminacion 18% — fuente, direccion, calidad, temperatura de color, sombras
  4. Accion      12% — verbo en presente, postura, energia del sujeto
  5. Composicion 10% — camara Sony A7III, lente 85mm f/2.0, encuadre
  6. Ambiente     7% — salon de grooming profesional, pared verde oscura
  7. Material     3% — textura del pelaje, brillo, detalles taciles

REGLAS ABSOLUTAS:
- Prosa narrativa completa en INGLES. NUNCA lista de keywords separados por comas.
- Objetivo: 150-200 palabras.
- PROHIBIDO usar estas palabras: masterpiece, best quality, highly detailed,
  ultra detailed, 4K, 8K, hyperrealistic, ultra HD, trending on ArtStation,
  high resolution, photorealistic (usar en su lugar el authority anchor).
- OBLIGATORIO terminar con un authority anchor de prestigio:
  "National Geographic wildlife portrait", "Sony World Photography Awards",
  "Pulitzer Prize-winning photograph", "shot for a Vogue Pets editorial".
- UN SOLO perro, 4 patas completamente visibles, anatomia perfecta.
- Sin texto, logotipos ni graficos dentro de la imagen.
- El perro debe verse recien baniado, pelaje limpio, brillante y arreglado.

TEMPLATE DE CONSTRUCCION:
[descriptor de raza + edad/tamano + color de pelaje + expresion + rasgo unico],
[detalle de grooming — pelaje limpio, cepillado, recortado],
[verbo de accion en presente] in [salon de grooming con pared verde oscura #1a6b3a],
[un micro-detalle sobre textura del pelaje o calidad del grooming].
Shot on [Sony A7III], [85mm f/2.0], [tipo de encuadre — medium close-up / portrait],
[direccion de luz + calidad + temperatura de color + comportamiento de sombras].
[Authority anchor — referencia de publicacion o premio fotografico de prestigio].

EJEMPLO DE PROMPT BIEN CONSTRUIDO:
"A three-year-old Poodle with freshly scissor-cut silver-white curls and bright dark eyes
catching the light sits perfectly still on a raised grooming table, gazing directly into
the lens with quiet confidence. The coat has the layered density of professional breed
trimming — each curl defined and springy, not a hair out of place. Sitting upright, chest
forward, in a professional dog grooming salon with a deep forest-green back wall.
The fur surface catches the light cleanly, revealing individual curl structure.
Shot on a Sony A7III with an 85mm f/2.0 lens, medium close-up framing that keeps all
four paws visible on the grooming table surface. Single large softbox positioned at
45 degrees camera-left produces even, flattering light with soft wraparound shadows
and a warm 5,000K color temperature that complements the salon's green tones.
A portrait that could anchor the cover of a leading European pet care magazine."
=== FIN DE FORMULA ===
"""


# ---------------------------------------------------------------------------
# Generacion de contenido con Claude + formula claude-banana
# ---------------------------------------------------------------------------

def claude_generate_content() -> dict:
    today = datetime.date.today()
    weekday = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"][today.weekday()]
    campaign = get_campaign_context(today)
    campaign_context = format_campaign_context_for_prompt(today)
    history_context = format_history_for_prompt()
    competitor_context = _load_competitor_insights()
    servicio_estrella = campaign["tema_mensual"]["servicio_estrella"]
    tipo_sugerido = suggest_content_type(servicio_estrella)

    # Elegir raza evitando las usadas recientemente
    razas_recientes = get_recent_breeds()
    breed_pool = [b for b in DOG_BREEDS if b not in razas_recientes] or DOG_BREEDS
    breed = breed_pool[today.timetuple().tm_yday % len(breed_pool)]

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=(
            "Eres el estratega y creador de contenido oficial de PetColinas en Instagram. "
            "Dominas la formula Portrait de claude-banana para generar prompts de imagen "
            "de calidad editorial. Produces contenido autentico dominicano que convierte. "
            "Siempre alineas el contenido con la campana de marketing activa del mes "
            "y respetas la rotacion de pilares para no repetir tipos de contenido."
        ),
        messages=[{
            "role": "user",
            "content": f"""Hoy es {weekday} {today.strftime('%d de %B de %Y')}.

{PETCOLINAS}

{campaign_context}

{history_context}

{competitor_context}

{PORTRAIT_FORMULA}

Tipos de post disponibles: {', '.join(CONTENT_TYPES)}
Tipo sugerido segun rotacion del plan: {tipo_sugerido}
Raza del dia: {breed}

Crea el contenido completo del post de Instagram de hoy.
INSTRUCCIONES:
- Usa el tipo sugerido segun rotacion SALVO que haya una fecha especial que justifique otro.
- El contenido DEBE estar alineado con el tema mensual y la campana trimestral activa.
- NO repitas razas marcadas como recientes en el historial.
- Si hay inteligencia competitiva disponible, usa las oportunidades para diferenciarte.
- Si hay una fecha especial hoy, incorporala de forma natural en el post.
Responde UNICAMENTE con JSON valido (sin markdown ni texto extra):

{{
  "tipo": "<tipo sugerido u otro justificado por fecha especial>",
  "tema": "<tema especifico alineado con la campana del mes, max 25 palabras>",
  "raza": "{breed}",
  "prompt_imagen": "<prompt de imagen COMPLETO en INGLES siguiendo la formula Portrait de claude-banana: prosa narrativa 150-200 palabras, 7 componentes ponderados, sin keywords prohibidas, con authority anchor al final. El perro es un {breed} recien baniado y arreglado en PetColinas.>",
  "caption": "<caption completo listo para Instagram: 1) linea gancho con emoji que detenga el scroll y refleje el tema del mes, 2) cuerpo 2-3 oraciones con tono dominicano calido, beneficio claro y la promocion del mes si aplica, 3) llamado a la accion directo, 4) contacto 809-752-6806 y Plaza Las Colinas, 5) 10-12 hashtags de la marca. Max 2200 caracteres.>"
}}"""
        }],
    )

    raw = response.content[0].text.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"Claude no retorno JSON valido:\n{raw}")
    return json.loads(match.group())


# ---------------------------------------------------------------------------
# Generacion de imagen con Stable Horde (red comunitaria, 100% gratuita)
# Sin necesidad de tarjeta de credito ni cuenta premium
# ---------------------------------------------------------------------------

def generate_image(image_prompt: str) -> bytes:
    horde_key = os.environ.get("HORDE_KEY", "0000000000")
    clean_prompt = " ".join(image_prompt.split())[:900]

    headers = {
        "apikey": horde_key,
        "Content-Type": "application/json",
        "Client-Agent": "petcolinas-bot:1.0:petcolinas@instagram",
    }
    payload = {
        "prompt": clean_prompt,
        "params": {
            "sampler_name": "k_euler_a",
            "cfg_scale": 7.5,
            "steps": 28,
            "width": 768,
            "height": 768,
            "n": 1,
        },
        "models": HORDE_MODELS,
        "nsfw": False,
        "r2": False,
    }

    print("  [Stable Horde] Enviando job a la red comunitaria...")
    resp = requests.post(f"{HORDE_API}/generate/async", json=payload, headers=headers, timeout=30)
    if resp.status_code != 202:
        raise RuntimeError(f"Horde rechazo el job: HTTP {resp.status_code} — {resp.text[:300]}")

    job_id = resp.json()["id"]
    print(f"  Job ID: {job_id}")

    for i in range(120):
        time.sleep(5)
        check = requests.get(f"{HORDE_API}/generate/check/{job_id}", timeout=15).json()
        if check.get("faulted"):
            raise RuntimeError("Stable Horde reporto un error en el job")
        if check.get("done"):
            print("  Imagen lista!")
            break
        wait = check.get("wait_time", "?")
        pos = check.get("queue_position", "?")
        if i % 6 == 0:
            print(f"  En cola: posicion {pos}, ETA {wait}s...")
    else:
        raise RuntimeError("Stable Horde timeout (10 min). Reintenta mas tarde.")

    status = requests.get(f"{HORDE_API}/generate/status/{job_id}", timeout=30).json()
    generations = status.get("generations", [])
    if not generations:
        raise RuntimeError("Horde no retorno ninguna imagen")

    img_bytes = base64.b64decode(generations[0]["img"])
    model_used = generations[0].get("model", "desconocido")
    print(f"  Generado con: {model_used} ({len(img_bytes):,} bytes)")

    img = Image.open(BytesIO(img_bytes)).convert("RGB")
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
    img = img.resize((1080, 1080), Image.LANCZOS)

    logo_path = "assets/logo_petcolinas.png"
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_w = 150
            logo_h = int(logo.height * (logo_w / logo.width))
            logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
            img.paste(logo, (1080 - logo_w - 20, 20), logo)
            print(f"  Logo superpuesto ({logo_w}x{logo_h}px)")
        except Exception as e:
            print(f"  Aviso: no se pudo agregar el logo ({e})")
    else:
        print("  Aviso: assets/logo_petcolinas.png no encontrado")

    output = BytesIO()
    img.save(output, format="JPEG", quality=95)
    return output.getvalue()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    today = datetime.date.today()
    campaign = get_campaign_context(today)
    from content_log import get_type_frequency
    freq = get_type_frequency()

    print(f"\n{'='*55}")
    print(f"  ORQUESTADOR PETCOLINAS — {today.strftime('%d/%m/%Y')}")
    print(f"  Usando formula Portrait de claude-banana")
    print(f"  Campana: {campaign['tema_mensual']['nombre']} ({campaign['trimestre']})")
    if campaign["es_fecha_especial"]:
        print(f"  Fecha especial: {campaign['evento_especial']['evento']}")
    if freq:
        print(f"  Posts ultimos 7 dias: { {k: v for k, v in freq.items()} }")
    print(f"{'='*55}\n")

    print("[Claude + claude-banana] Generando contenido del dia...")
    content = claude_generate_content()
    print(f"  Tipo   : {content['tipo']}")
    print(f"  Tema   : {content['tema']}")
    print(f"  Raza   : {content.get('raza', 'N/A')}")
    print(f"  Prompt : {content['prompt_imagen'][:120]}...")
    print(f"  Caption: {content['caption'][:80]}...")

    print("\n[Stable Horde] Generando imagen editorial 1080x1080...")
    image_bytes = generate_image(content["prompt_imagen"])

    with open("post_del_dia.jpg", "wb") as f:
        f.write(image_bytes)
    print(f"  Imagen guardada: post_del_dia.jpg ({len(image_bytes):,} bytes)")

    with open("caption.txt", "w", encoding="utf-8") as f:
        f.write(content["caption"])
    print("  Caption guardado: caption.txt")

    append_post(
        tipo=content["tipo"],
        tema=content["tema"],
        raza=content.get("raza", "N/A"),
        mes_campana=campaign["tema_mensual"]["nombre"],
    )
    print("  Historial actualizado: content_log.json")

    print("\nContenido listo. El workflow publicara en Instagram.")


if __name__ == "__main__":
    main()
