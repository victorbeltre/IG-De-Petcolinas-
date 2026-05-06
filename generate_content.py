"""
Orquestador automatico de contenido para PetColinas.
Claude + formula Portrait claude-banana + Nano Banana 2 (Gemini imagen 2K).

Genera dos archivos en el directorio actual:
  post_del_dia.jpg  -> imagen 1080x1080 JPEG con logo de PetColinas
  caption.txt       -> caption listo para Instagram

Variables de entorno requeridas:
  ANTHROPIC_API_KEY  -> API key de Claude (Anthropic)
  GEMINI_API_KEY     -> API key de Google AI Studio (para Nano Banana 2)
"""

import os
import sys
import json
import re
import datetime
from io import BytesIO

import anthropic
import google.generativeai as genai
from PIL import Image

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

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
# Formula Portrait de claude-banana (7 componentes)
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
- PROHIBIDO: masterpiece, best quality, highly detailed, ultra detailed,
  4K, 8K, hyperrealistic, ultra HD, trending on ArtStation, high resolution.
- OBLIGATORIO terminar con authority anchor de prestigio:
  "National Geographic wildlife portrait", "Sony World Photography Awards",
  "Pulitzer Prize-winning photograph", "shot for a Vogue Pets editorial".
- UN SOLO perro, 4 patas completamente visibles, anatomia perfecta.
- Sin texto, logotipos ni graficos dentro de la imagen.
- El perro debe verse recien baniado, pelaje limpio y arreglado.
=== FIN DE FORMULA ===
"""


# ---------------------------------------------------------------------------
# Paso 1 — Claude genera estrategia, prompt y caption
# ---------------------------------------------------------------------------

def claude_generate_content() -> dict:
    today = datetime.date.today()
    weekday = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"][today.weekday()]
    breed = DOG_BREEDS[today.timetuple().tm_yday % len(DOG_BREEDS)]

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=(
            "Eres el estratega y creador de contenido oficial de PetColinas en Instagram. "
            "Dominas la formula Portrait de claude-banana para generar prompts de imagen "
            "de calidad editorial. Produces contenido autentico dominicano que convierte."
        ),
        messages=[{
            "role": "user",
            "content": f"""Hoy es {weekday} {today.strftime('%d de %B de %Y')}.

{PETCOLINAS}

{PORTRAIT_FORMULA}

Tipos de post disponibles: {', '.join(CONTENT_TYPES)}
Raza del dia: {breed}

Crea el contenido completo del post de Instagram de hoy.
Responde UNICAMENTE con JSON valido (sin markdown ni texto extra):

{{
  "tipo": "<uno de los tipos listados>",
  "tema": "<tema especifico, max 25 palabras>",
  "prompt_imagen": "<prompt COMPLETO en INGLES siguiendo la formula Portrait de claude-banana: prosa narrativa 150-200 palabras, 7 componentes ponderados, sin keywords prohibidas, con authority anchor al final. El perro es un {breed} recien baniado en PetColinas.>",
  "caption": "<caption completo: 1) gancho con emoji, 2) cuerpo dominicano calido, 3) CTA directo, 4) contacto 809-752-6806 y Plaza Las Colinas, 5) 10-12 hashtags. Max 2200 chars.>"
}}"""
        }],
    )

    raw = response.content[0].text.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"Claude no retorno JSON valido:\n{raw}")
    return json.loads(match.group())


# ---------------------------------------------------------------------------
# Paso 2 — Nano Banana 2 genera la imagen (gemini-3.1-flash-image-preview)
# ---------------------------------------------------------------------------

def generate_image(image_prompt: str) -> bytes:
    """Genera imagen 2K con Nano Banana 2 y superpone el logo de PetColinas."""
    print("  Generando con Nano Banana 2 (gemini-3.1-flash-image-preview) @ 2K...")

    model = genai.GenerativeModel("gemini-3.1-flash-image-preview")
    response = model.generate_content(
        image_prompt,
        generation_config={
            "response_modalities": ["IMAGE"],
            "image_size": "2K",
        },
    )

    # Extraer bytes de imagen de la respuesta
    raw_bytes = None
    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data.mime_type.startswith("image/"):
            raw_bytes = part.inline_data.data
            break

    if not raw_bytes:
        raise Exception(
            "Nano Banana 2 no retorno imagen. Respuesta: "
            + str(response.candidates[0].content.parts)
        )

    # Recortar a cuadrado y redimensionar a 1080x1080
    img = Image.open(BytesIO(raw_bytes)).convert("RGB")
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
    img = img.resize((1080, 1080), Image.LANCZOS)
    print(f"  Imagen recortada y redimensionada a 1080x1080")

    # Superponer logo en esquina superior derecha
    logo_path = "assets/logo_petcolinas.png"
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_w = 150
            logo_h = int(logo.height * (logo_w / logo.width))
            logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
            img.paste(logo, (1080 - logo_w - 20, 20), logo)
            print(f"  Logo superpuesto ({logo_w}x{logo_h}px) en esquina superior derecha")
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
    print(f"\n{'='*55}")
    print(f"  ORQUESTADOR PETCOLINAS — {today.strftime('%d/%m/%Y')}")
    print(f"  Claude + claude-banana + Nano Banana 2")
    print(f"{'='*55}\n")

    print("[Claude + claude-banana] Generando contenido del dia...")
    content = claude_generate_content()
    print(f"  Tipo   : {content['tipo']}")
    print(f"  Tema   : {content['tema']}")
    print(f"  Prompt : {content['prompt_imagen'][:120]}...")
    print(f"  Caption: {content['caption'][:80]}...")

    print("\n[Nano Banana 2] Generando imagen editorial...")
    image_bytes = generate_image(content["prompt_imagen"])

    with open("post_del_dia.jpg", "wb") as f:
        f.write(image_bytes)
    print(f"  Guardado: post_del_dia.jpg ({len(image_bytes):,} bytes)")

    with open("caption.txt", "w", encoding="utf-8") as f:
        f.write(content["caption"])
    print("  Guardado: caption.txt")

    print("\nContenido listo. El workflow publicara en Instagram.")


if __name__ == "__main__":
    main()
