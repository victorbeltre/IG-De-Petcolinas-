"""
Orquestador automatico de contenido para PetColinas.

Flujo:
  1. Claude          -> Decide el tema del post y genera el prompt de imagen
  2. Pollinations.ai -> Genera imagen 1080x1080 con FLUX (gratis, sin API key)
  3. Claude          -> Genera el caption en voz dominicana
  4. GitHub          -> Sube post_del_dia.jpg al repo
  5. GitHub Actions  -> run_bot.yml publica en @petcolinas

Variables de entorno requeridas:
  ANTHROPIC_API_KEY  -> API key de Claude (Anthropic)
  GITHUB_PAT         -> GitHub Personal Access Token (repo + workflow)
"""

import os
import sys
import json
import re
import datetime
import urllib.parse
from io import BytesIO

import anthropic
import requests
from PIL import Image

from gemini_trigger import upload_image_and_publish

# ---------------------------------------------------------------------------
# Cliente Claude
# ---------------------------------------------------------------------------

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# ---------------------------------------------------------------------------
# Contexto de marca PetColinas
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

CONTENT_TYPES = [
    "grooming",
    "veterinaria",
    "membresia",
    "educativo",
    "urgencia",
    "antes_despues",
]


# ---------------------------------------------------------------------------
# Paso 1 — Claude decide el tema y genera todo el contenido de texto
# ---------------------------------------------------------------------------

def claude_generate_content() -> dict:
    today = datetime.date.today()
    weekday = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"][today.weekday()]

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=(
            "Eres el estratega y creador de contenido oficial de PetColinas en Instagram. "
            "Creativo, conoces el mercado dominicano, generas contenido que convierte seguidores en clientes."
        ),
        messages=[{
            "role": "user",
            "content": f"""Hoy es {weekday} {today.strftime('%d de %B de %Y')}.

{PETCOLINAS}

Tipos de post: {', '.join(CONTENT_TYPES)}

Crea el contenido completo para el post de Instagram de hoy.
Responde UNICAMENTE con JSON valido (sin markdown, sin texto extra):

{{
  "tipo": "<uno de los tipos listados>",
  "tema": "<descripcion especifica del tema, max 25 palabras>",
  "prompt_imagen": "<prompt en INGLES para generar imagen con IA FLUX. Describe escena: perro feliz y bien arreglado, ambiente de peluqueria canina profesional, colores verde oscuro y naranja, iluminacion calida, fondo limpio, fotografia de alta calidad. Max 80 palabras.>",
  "caption": "<caption completo listo para Instagram. Estructura: 1) linea gancho con emoji que detiene el scroll, 2) cuerpo 2-3 oraciones con beneficio principal en tono dominicano calido, 3) CTA claro, 4) contacto con emoji 809-752-6806 y Plaza Las Colinas, 5) 10-12 hashtags al final. Max 2200 caracteres.>"
}}"""
        }],
    )

    raw = response.content[0].text.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"Claude no retorno JSON valido:\n{raw}")
    return json.loads(match.group())


# ---------------------------------------------------------------------------
# Paso 2 — Pollinations.ai genera la imagen (FLUX, gratis, sin API key)
# ---------------------------------------------------------------------------

def generate_image(image_prompt: str) -> bytes:
    seed = int(datetime.date.today().strftime("%Y%m%d"))

    full_prompt = (
        "professional pet grooming salon, happy well-groomed dog, "
        "dark green and warm orange brand colors, soft warm lighting, "
        "clean modern interior, high quality photography, Instagram post. "
        + image_prompt
    )[:500]

    encoded = urllib.parse.quote(full_prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1080&height=1080&model=flux&nologo=true&seed={seed}"
    )

    print("  Generando con FLUX (Pollinations.ai)...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()

    img = Image.open(BytesIO(resp.content))
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
    img = img.resize((1080, 1080), Image.LANCZOS)

    output = BytesIO()
    img.convert("RGB").save(output, format="JPEG", quality=95)
    return output.getvalue()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    today = datetime.date.today()
    print(f"\n{'='*50}")
    print(f"  ORQUESTADOR PETCOLINAS — {today.strftime('%d/%m/%Y')}")
    print(f"{'='*50}\n")

    print("[Claude] Generando estrategia, tema y caption del dia...")
    content = claude_generate_content()
    print(f"  Tipo   : {content['tipo']}")
    print(f"  Tema   : {content['tema']}")
    print(f"  Caption: {content['caption'][:80]}...")

    print("\n[FLUX] Generando imagen 1080x1080...")
    image_bytes = generate_image(content["prompt_imagen"])
    image_path = "/tmp/post_del_dia.jpg"
    with open(image_path, "wb") as f:
        f.write(image_bytes)
    print(f"  Imagen lista: {len(image_bytes):,} bytes")

    print("\n[GitHub] Subiendo imagen y disparando workflow de Instagram...")
    success = upload_image_and_publish(image_path=image_path, caption=content["caption"])

    print()
    if success:
        print("POST PUBLICADO EN @petcolinas CON EXITO")
    else:
        print("ERROR: Revisar logs de GitHub Actions")
        sys.exit(1)


if __name__ == "__main__":
    main()
