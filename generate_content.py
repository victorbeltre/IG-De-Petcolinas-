"""
Orquestador automatico de contenido para PetColinas.

Genera dos archivos en el directorio actual:
  post_del_dia.jpg  -> imagen 1080x1080 JPEG con logo de PetColinas
  caption.txt       -> caption listo para Instagram

El workflow de GitHub Actions (daily_content.yml) se encarga de:
  - Hacer commit y push de la imagen
  - Publicar en Instagram via publish_to_ig.py

Variable de entorno requerida:
  ANTHROPIC_API_KEY  -> API key de Claude (Anthropic)
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

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

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


def claude_generate_content() -> dict:
    today = datetime.date.today()
    weekday = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"][today.weekday()]

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=(
            "Eres el estratega y creador de contenido oficial de PetColinas en Instagram. "
            "Creativo, conoces el mercado dominicano, generas contenido que convierte."
        ),
        messages=[{
            "role": "user",
            "content": f"""Hoy es {weekday} {today.strftime('%d de %B de %Y')}.

{PETCOLINAS}

Tipos de post: {', '.join(CONTENT_TYPES)}

Crea el contenido completo del post de Instagram de hoy.
Responde UNICAMENTE con JSON valido (sin markdown ni texto extra):

{{
  "tipo": "<uno de los tipos listados>",
  "tema": "<tema especifico, max 25 palabras>",
  "prompt_imagen": "<prompt profesional en INGLES para generar foto realista de perro en peluqueria. Incluir: raza especifica (ej: Golden Retriever, Poodle, Shih Tzu), grooming profesional de alta calidad, salon limpio y moderno, iluminacion natural suave y profesional, colores de fondo en verde oscuro y naranja (marca), perro feliz y relajado, fotografia de revista profesional, ultra realista, sin errores, sin deformidades. Max 100 palabras.>",
  "caption": "<caption completo listo para Instagram: 1) linea gancho con emoji, 2) cuerpo 2-3 oraciones tono dominicano calido, 3) CTA claro, 4) contacto 809-752-6806 y Plaza Las Colinas, 5) 10-12 hashtags. Max 2200 caracteres.>"
}}"""
        }],
    )

    raw = response.content[0].text.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"Claude no retorno JSON valido:\n{raw}")
    return json.loads(match.group())


def generate_image(image_prompt: str) -> bytes:
    """Genera imagen realista con FLUX + superpone logo de PetColinas."""
    seed = int(datetime.date.today().strftime("%Y%m%d"))
    
    # Prompt mejorado: énfasis en realismo y detalle
    full_prompt = (
        "ultra realistic professional photography, high quality, studio lighting, "
        "perfect composition, sharp focus, no deformities, no anatomical errors, "
        "magazine quality pet grooming photograph. "
        + image_prompt
    )[:600]

    encoded = urllib.parse.quote(full_prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1080&height=1080&model=flux&nologo=true&seed={seed}"
    )

    print("  Generando con FLUX (Pollinations.ai)...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()

    img = Image.open(BytesIO(resp.content)).convert("RGB")
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
    img = img.resize((1080, 1080), Image.LANCZOS)

    # Agregar logo si existe
    try:
        if os.path.exists("assets/logo_petcolinas.png"):
            logo = Image.open("assets/logo_petcolinas.png").convert("RGBA")
            # Redimensionar logo a 120x120 (esquina superior derecha)
            logo = logo.resize((120, 120), Image.LANCZOS)
            # Pegar en esquina superior derecha con margen de 15px
            img.paste(logo, (1080 - 120 - 15, 15), logo)
            print("  Logo agregado a la imagen")
    except Exception as e:
        print(f"  Aviso: no se pudo agregar el logo ({e})")

    output = BytesIO()
    img.save(output, format="JPEG", quality=95)
    return output.getvalue()


def main():
    today = datetime.date.today()
    print(f"\n{'='*50}")
    print(f"  ORQUESTADOR PETCOLINAS — {today.strftime('%d/%m/%Y')}")
    print(f"{'='*50}\n")

    print("[Claude] Generando estrategia, tema y caption...")
    content = claude_generate_content()
    print(f"  Tipo   : {content['tipo']}")
    print(f"  Tema   : {content['tema']}")
    print(f"  Caption: {content['caption'][:80]}...")

    print("\n[FLUX] Generando imagen realista 1080x1080...")
    image_bytes = generate_image(content["prompt_imagen"])

    with open("post_del_dia.jpg", "wb") as f:
        f.write(image_bytes)
    print(f"  Imagen guardada: post_del_dia.jpg ({len(image_bytes):,} bytes)")

    with open("caption.txt", "w", encoding="utf-8") as f:
        f.write(content["caption"])
    print("  Caption guardado: caption.txt")

    print("\nContenido listo. El workflow publicara en Instagram.")


if __name__ == "__main__":
    main()
