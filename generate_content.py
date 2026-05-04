"""
Orquestador automatico de contenido para PetColinas.

Flujo:
  1. Claude  -> Decide el tema del post del dia y genera el prompt para Gemini
  2. Gemini  -> Genera la imagen 1080x1080 y el caption draft
  3. Claude  -> Revisa y refina el caption con voz dominicana autentica
  4. GitHub  -> Sube post_del_dia.jpg al repo (via gemini_trigger.py)
  5. GitHub Actions -> run_bot.yml publica en @petcolinas en Instagram

Variables de entorno requeridas:
  ANTHROPIC_API_KEY   -> API key de Claude (Anthropic)
  GEMINI_API_KEY      -> API key de Google Gemini
  GITHUB_PAT          -> GitHub Personal Access Token (repo + workflow)
"""

import os
import sys
import json
import re
import datetime
from io import BytesIO

import anthropic
from google import genai as google_genai
from google.genai import types as google_types
from PIL import Image

from gemini_trigger import upload_image_and_publish

# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
gemini = google_genai.Client(api_key=os.environ["GEMINI_API_KEY"])

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

COLORES DE MARCA: Verde oscuro #1a6b3a | Verde medio #2d8f52 | Naranja #d45f1e | Dorado #c9a227

ESTILO: Calido, dominicano, cercano. Frases como "peludito", "nube de algodon",
  "bajo a perro", "tu peludo merece lo mejor". Nunca demasiado corporativo.

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
# Paso 1 — Claude decide el tema del dia
# ---------------------------------------------------------------------------

def claude_decide_theme() -> dict:
    today = datetime.date.today()
    weekday = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"][today.weekday()]

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=900,
        system=(
            "Eres el estratega de marketing digital de PetColinas. "
            "Creativo, estrategico, conoces el mercado dominicano."
        ),
        messages=[{
            "role": "user",
            "content": f"""Hoy es {weekday} {today.strftime('%d de %B de %Y')}.

{PETCOLINAS}

Tipos de post disponibles: {', '.join(CONTENT_TYPES)}

Elige el tipo de post mas efectivo para hoy y disena el contenido.
Responde UNICAMENTE con un JSON valido con esta estructura exacta (sin markdown, sin texto extra):

{{
  "tipo": "<uno de los tipos listados>",
  "tema": "<descripcion del tema especifico, maximo 25 palabras>",
  "prompt_imagen": "<prompt en INGLES para Gemini 2.0 Flash image generation. Pide una imagen cuadrada 1:1 de un perro feliz y bien arreglado en una peluqueria canina profesional, colores verde oscuro y naranja, iluminacion calida, ambiente limpio. Incluye en la imagen texto en espanol con el nombre PetColinas y el numero 809-752-6806. Maximo 150 palabras.>",
  "guia_caption": "<instrucciones para Gemini sobre tono, angulo y que incluir en el caption. Maximo 40 palabras.>"
}}"""
        }],
    )

    raw = response.content[0].text.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"Claude no retorno JSON valido:\n{raw}")
    return json.loads(match.group())


# ---------------------------------------------------------------------------
# Paso 2a — Gemini genera la imagen (Gemini 2.0 Flash, gratis con API key)
# ---------------------------------------------------------------------------

def gemini_generate_image(image_prompt: str) -> bytes:
    full_prompt = (
        "Generate a square 1:1 aspect ratio image optimized for Instagram (1080x1080 pixels). "
        + image_prompt
    )

    response = gemini.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=full_prompt,
        config=google_types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"]
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            img = Image.open(BytesIO(part.inline_data.data))
            # Recortar al cuadrado central y redimensionar a 1080x1080
            w, h = img.size
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            img = img.crop((left, top, left + side, top + side))
            img = img.resize((1080, 1080), Image.LANCZOS)

            output = BytesIO()
            img.convert("RGB").save(output, format="JPEG", quality=95)
            return output.getvalue()

    raise ValueError("Gemini no genero ninguna imagen en la respuesta")


# ---------------------------------------------------------------------------
# Paso 2b — Gemini genera el caption draft
# ---------------------------------------------------------------------------

def gemini_generate_caption(theme: dict) -> str:
    response = gemini.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"""Eres el creador de contenido de PetColinas en Instagram.

{PETCOLINAS}

Tema del post de hoy: {theme['tema']}
Guia de contenido: {theme['guia_caption']}

Genera un caption para Instagram con esta estructura:
1. Primera linea gancho (detiene el scroll, maximo 10 palabras, usa emoji)
2. Cuerpo (2-3 oraciones con el beneficio o informacion principal)
3. Llamado a la accion claro
4. Contacto: 📱 809-752-6806 | 📍 Plaza Las Colinas
5. Hashtags relevantes (10-12 hashtags al final)

Responde SOLO con el caption completo, listo para pegar en Instagram.""",
    )
    return response.text.strip()


# ---------------------------------------------------------------------------
# Paso 3 — Claude refina el caption
# ---------------------------------------------------------------------------

def claude_refine_caption(caption_draft: str, theme: dict) -> str:
    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        system=(
            "Eres el editor de contenido de PetColinas. "
            "Refinas captions para Instagram con voz dominicana autentica y calida."
        ),
        messages=[{
            "role": "user",
            "content": f"""Revisa este caption de Instagram para PetColinas.

Tema: {theme['tema']}

Caption de Gemini:
{caption_draft}

Criterios:
- Voz dominicana natural ("peludito", "bajo a perro", etc. si aplica)
- Primera linea que detiene el scroll
- CTA claro con WhatsApp 809-752-6806
- Emojis naturales, no exagerados (maximo 8-10)
- Maximo 2200 caracteres
- Hashtags de marca al final

Si esta excelente, returnalo sin cambios. Si necesita mejoras, returnalo mejorado.
Responde SOLO con el caption final.""",
        }],
    )
    return response.content[0].text.strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    today = datetime.date.today()
    print(f"\n{'='*50}")
    print(f"  ORQUESTADOR PETCOLINAS — {today.strftime('%d/%m/%Y')}")
    print(f"{'='*50}\n")

    print("[Claude] Decidiendo tema del post del dia...")
    theme = claude_decide_theme()
    print(f"  Tipo  : {theme['tipo']}")
    print(f"  Tema  : {theme['tema']}")

    print("\n[Gemini 2.0 Flash] Generando imagen 1080x1080...")
    image_bytes = gemini_generate_image(theme["prompt_imagen"])
    image_path = "/tmp/post_del_dia.jpg"
    with open(image_path, "wb") as f:
        f.write(image_bytes)
    print(f"  Imagen generada: {len(image_bytes):,} bytes")

    print("\n[Gemini] Generando caption draft...")
    caption_draft = gemini_generate_caption(theme)
    print(f"  Draft: {caption_draft[:80]}...")

    print("\n[Claude] Refinando caption...")
    caption_final = claude_refine_caption(caption_draft, theme)
    print(f"  Final: {caption_final[:80]}...")

    print("\n[GitHub] Subiendo imagen al repo y disparando workflow...")
    success = upload_image_and_publish(image_path=image_path, caption=caption_final)

    print()
    if success:
        print("POST PUBLICADO EN @petcolinas CON EXITO")
    else:
        print("ERROR: Revisar logs de GitHub Actions")
        sys.exit(1)


if __name__ == "__main__":
    main()
