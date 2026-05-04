"""
Orquestador automatico de contenido para PetColinas.

Genera dos archivos en el directorio actual:
  post_del_dia.jpg  -> imagen 1080x1080 JPEG con logo de PetColinas
  caption.txt       -> caption listo para Instagram

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

# Razas realistas que FLUX maneja bien (anatomia correcta)
DOG_BREEDS = [
    "Golden Retriever", "Labrador Retriever", "Poodle", "Shih Tzu",
    "Maltese", "French Bulldog", "Bichon Frise", "Cocker Spaniel",
    "Schnauzer", "Yorkshire Terrier", "Havanese", "Pomeranian"
]


def claude_generate_content() -> dict:
    today = datetime.date.today()
    weekday = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"][today.weekday()]
    # Raza del dia (rotacion por dia del ano)
    breed = DOG_BREEDS[today.timetuple().tm_yday % len(DOG_BREEDS)]

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
Raza del dia para la imagen: {breed}

Crea el contenido completo del post de Instagram de hoy.
Responde UNICAMENTE con JSON valido (sin markdown ni texto extra):

{{
  "tipo": "<uno de los tipos listados>",
  "tema": "<tema especifico, max 25 palabras>",
  "prompt_imagen": "<prompt HIPER REALISTA en INGLES para {breed}. Escena concreta y simple: el perro sentado quieto mirando a camara, recien baniado y arreglado, pelo limpio y brillante, salon de grooming con pared verde oscura, iluminacion de ventana lateral suave. Camara: Sony A7 85mm f2.0, bokeh suave. Especificar SOLO UN perro, 4 patas visibles, anatomia perfecta, foto de alta gama, sin texto en la imagen. Max 80 palabras.>",
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
    """Genera imagen hiper-realista con flux-realism + superpone logo."""
    seed = int(datetime.date.today().strftime("%Y%m%d"))

    # Prefix tecnico de fotografia para maximo realismo
    photo_prefix = (
        "hyperrealistic DSLR photography, Sony A7III, 85mm portrait lens, f/2.0 aperture, "
        "natural window light, shallow depth of field, photojournalism quality, "
        "National Geographic style, skin and fur texture detail, no AI artifacts, "
        "no plastic look, no over-smoothing, raw unedited feel. "
    )

    full_prompt = (photo_prefix + image_prompt)[:700]
    encoded = urllib.parse.quote(full_prompt)

    # flux-realism: modelo especifico para fotorrealismo en Pollinations.ai
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1080&height=1080&model=flux-realism&nologo=true&seed={seed}&enhance=true"
    )

    print("  Generando con FLUX-REALISM (Pollinations.ai)...")
    resp = requests.get(url, timeout=180)
    resp.raise_for_status()

    img = Image.open(BytesIO(resp.content)).convert("RGB")
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
    img = img.resize((1080, 1080), Image.LANCZOS)

    # Superponer logo en esquina superior derecha
    logo_path = "assets/logo_petcolinas.png"
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            # Logo a 150px de ancho manteniendo proporciones
            logo_w = 150
            ratio = logo_w / logo.width
            logo_h = int(logo.height * ratio)
            logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
            # Esquina superior derecha con margen 20px
            x = 1080 - logo_w - 20
            y = 20
            img.paste(logo, (x, y), logo)
            print(f"  Logo superpuesto ({logo_w}x{logo_h}px) en esquina superior derecha")
        except Exception as e:
            print(f"  Aviso: no se pudo agregar el logo ({e})")
    else:
        print("  Aviso: assets/logo_petcolinas.png no encontrado, imagen sin logo")

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

    print("\n[FLUX-REALISM] Generando imagen hiper-realista 1080x1080...")
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
