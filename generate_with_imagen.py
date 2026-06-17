#!/usr/bin/env python3
"""
generate_with_imagen.py
Genera carruseles de Instagram con fondos de Google Imagen + branding PetColinas.

Flujo:
  1. Lee carrusel_config.json con la definición del carrusel
  2. Genera un fondo único por slide con Google Imagen API
  3. Superpone logo, colores y texto de PetColinas con Pillow
  4. Guarda slides en posts/<folder>/  y crea caption.txt

Requerido:
  export GOOGLE_AI_KEY="AIza..."
  pip install google-genai pillow

Uso:
  python generate_with_imagen.py               # lee carrusel_config.json
  python generate_with_imagen.py --dry-run     # genera sin llamar a Imagen (usa fondos de color)
"""

import os
import sys
import json
import time
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Dimensiones ───────────────────────────────────────────────────────────────
W = H = 1080

# ── Colores PetColinas ────────────────────────────────────────────────────────
VERDE      = "#1a6b3a"
VERDE_DARK = "#145230"
NARANJA    = "#d45f1e"
DORADO     = "#c9a227"
BLANCO     = "#ffffff"
NEGRO      = "#111111"

def rgb(hex_color: str, alpha: int = 255) -> tuple:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, alpha)

def rgb3(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

# ── Fuentes ───────────────────────────────────────────────────────────────────
_FONT_DIR  = Path("/usr/share/fonts/truetype/dejavu")
_FONT_BOLD = str(_FONT_DIR / "DejaVuSans-Bold.ttf")
_FONT_REG  = str(_FONT_DIR / "DejaVuSans.ttf")

def fnt(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_FONT_BOLD if bold else _FONT_REG, size)

# ── Google Imagen ─────────────────────────────────────────────────────────────
_DRY_RUN = "--dry-run" in sys.argv

def _dry_background(prompt: str) -> Image.Image:
    """Fondo de color para modo dry-run (sin API)."""
    img = Image.new("RGBA", (W, H), rgb3(VERDE_DARK) + (255,))
    draw = ImageDraw.Draw(img)
    for i in range(0, W, 60):
        draw.line([(i, 0), (i, H)], fill=(*rgb3(VERDE), 30), width=1)
    for j in range(0, H, 60):
        draw.line([(0, j), (W, j)], fill=(*rgb3(VERDE), 30), width=1)
    return img

def generate_bg(prompt: str, fast: bool = False) -> Image.Image:
    """Genera un fondo 1080x1080 con Google Imagen via REST API."""
    if _DRY_RUN:
        print("    [dry-run] Saltando llamada a Imagen API")
        return _dry_background(prompt)

    import requests as _req

    api_key = os.environ.get("GOOGLE_AI_KEY")
    if not api_key:
        print("ERROR: Falta GOOGLE_AI_KEY en el entorno.")
        print("       export GOOGLE_AI_KEY='AIza...'")
        sys.exit(1)

    model = "imagen-3.0-fast-generate-001" if fast else "imagen-3.0-generate-001"
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:predict?key={api_key}"
    )

    full_prompt = (
        f"{prompt}. "
        "Professional photography, vibrant colors, clean composition, "
        "no text, no watermarks, no overlaid captions, high quality."
    )

    payload = {
        "instances": [{"prompt": full_prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "1:1",
            "safetyFilterLevel": "block_only_high",
            "personGeneration": "dont_allow",
        },
    }

    for attempt in range(3):
        try:
            resp = _req.post(url, json=payload, timeout=90)
            resp.raise_for_status()
            data = resp.json()
            b64 = data["predictions"][0]["bytesBase64Encoded"]
            import base64
            img_bytes = base64.b64decode(b64)
            img = Image.open(BytesIO(img_bytes)).convert("RGBA")
            return img.resize((W, H), Image.LANCZOS)
        except Exception as e:
            print(f"    Intento {attempt+1}/3 falló: {e}")
            if attempt < 2:
                time.sleep(8)
    print("    ERROR: No se pudo generar el fondo después de 3 intentos.")
    sys.exit(1)

# ── Utilidades de dibujo ──────────────────────────────────────────────────────
def overlay(img: Image.Image, opacity: int = 155) -> Image.Image:
    """Capa oscura semitransparente para legibilidad."""
    mask = Image.new("RGBA", img.size, (0, 0, 0, opacity))
    return Image.alpha_composite(img.convert("RGBA"), mask)

def verde_band(img: Image.Image, y: int, h: int, color: str = VERDE, alpha: int = 220) -> Image.Image:
    band = Image.new("RGBA", (W, h), rgb(color, alpha))
    img.paste(band, (0, y), band)
    return img

def add_logo(img: Image.Image, size: int = 120, x_anchor: str = "right", y: int = 30) -> Image.Image:
    logo_path = Path("assets/logo_petcolinas.png")
    if not logo_path.exists():
        return img
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((size, size), Image.LANCZOS)
    margin = 30
    x = W - size - margin if x_anchor == "right" else margin
    img.paste(logo, (x, y), logo)
    return img

def wrap(text: str, fnt_obj: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        if fnt_obj.getlength(test) <= max_w:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines

def footer_bar(img: Image.Image) -> Image.Image:
    img = verde_band(img, H - 72, 72, VERDE_DARK, alpha=230)
    draw = ImageDraw.Draw(img)
    draw.text(
        (W // 2, H - 36),
        "🐾  PetColinas  ·  Plaza Las Colinas, SDO Oeste  ·  @petcolinasrd",
        font=fnt(24, bold=False),
        fill=rgb(BLANCO),
        anchor="mm",
    )
    return img

# ── Renderizadores por tipo de slide ─────────────────────────────────────────
def render_portada(bg: Image.Image, slide: dict) -> Image.Image:
    """Slide 1: logo centrado grande + título + subtítulo."""
    img = overlay(bg, opacity=140)

    # Logo centrado
    logo_size = 200
    logo_path = Path("assets/logo_petcolinas.png")
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        img.paste(logo, ((W - logo_size) // 2, 160), logo)

    draw = ImageDraw.Draw(img)

    # Título
    titulo = slide.get("titulo", "").upper()
    lines = wrap(titulo, fnt(76), W - 120)
    y = 430
    for line in lines:
        draw.text((W // 2, y), line, font=fnt(76), fill=rgb(BLANCO),
                  anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0, 200))
        y += 90

    # Subtítulo
    sub = slide.get("subtitulo", "")
    if sub:
        draw.text((W // 2, y + 20), sub, font=fnt(44, bold=False),
                  fill=rgb(DORADO), anchor="mm")

    # Acento naranja
    banda = Image.new("RGBA", (W, 8), rgb(NARANJA))
    img.paste(banda, (0, H - 80), banda)

    return footer_bar(img)


def render_contenido(bg: Image.Image, slide: dict) -> Image.Image:
    """Slide de contenido: barra de título + puntos."""
    img = overlay(bg, opacity=165)
    img = add_logo(img, size=100, x_anchor="right", y=28)

    # Barra de título
    img = verde_band(img, 70, 108, VERDE, alpha=230)
    draw = ImageDraw.Draw(img)
    draw.text(
        (W // 2, 70 + 54), slide.get("titulo", "").upper(),
        font=fnt(48), fill=rgb(BLANCO), anchor="mm",
    )

    # Puntos
    puntos = slide.get("puntos", [])
    y = 220
    for punto in puntos:
        lineas = wrap(f"✦  {punto}", fnt(38, bold=False), W - 160)
        for linea in lineas:
            draw.text((70, y), linea, font=fnt(38, bold=False), fill=rgb(BLANCO))
            y += 52
        y += 16

    return footer_bar(img)


def render_dos_col(bg: Image.Image, slide: dict) -> Image.Image:
    """Slide con dos columnas de info (ej: comparación de planes)."""
    img = overlay(bg, opacity=175)
    img = add_logo(img, size=90, x_anchor="right", y=20)

    draw = ImageDraw.Draw(img)

    # Encabezado
    img = verde_band(img, 60, 100, VERDE, alpha=230)
    draw = ImageDraw.Draw(img)
    draw.text(
        (W // 2, 110), slide.get("titulo", "").upper(),
        font=fnt(46), fill=rgb(BLANCO), anchor="mm",
    )

    col_izq = slide.get("col_izq", {})
    col_der = slide.get("col_der", {})

    col_w = W // 2 - 60

    for idx, col in enumerate([col_izq, col_der]):
        x_base = 60 if idx == 0 else W // 2 + 20
        color_header = NARANJA if idx == 0 else DORADO

        # Header columna
        band = Image.new("RGBA", (col_w, 60), rgb(color_header, 220))
        img.paste(band, (x_base, 185), band)
        draw = ImageDraw.Draw(img)
        draw.text(
            (x_base + col_w // 2, 215), col.get("header", ""),
            font=fnt(36), fill=rgb(BLANCO), anchor="mm",
        )

        # Items
        y = 270
        for item in col.get("items", []):
            lineas = wrap(f"• {item}", fnt(30, bold=False), col_w - 10)
            for linea in lineas:
                draw.text((x_base + 8, y), linea, font=fnt(30, bold=False), fill=rgb(BLANCO))
                y += 44
            y += 8

    return footer_bar(img)


def render_precio(bg: Image.Image, slide: dict) -> Image.Image:
    """Slide de precio destacado."""
    img = overlay(bg, opacity=155)
    img = add_logo(img, size=110, x_anchor="right", y=28)

    draw = ImageDraw.Draw(img)

    # Nombre del plan
    nombre = slide.get("nombre_plan", "")
    img = verde_band(img, 80, 110, VERDE, alpha=235)
    draw = ImageDraw.Draw(img)
    draw.text((W // 2, 135), nombre.upper(), font=fnt(52), fill=rgb(BLANCO), anchor="mm")

    # Precio
    precio = slide.get("precio", "")
    precio_box = Image.new("RGBA", (500, 110), rgb(NARANJA, 230))
    img.paste(precio_box, ((W - 500) // 2, 220), precio_box)
    draw = ImageDraw.Draw(img)
    draw.text((W // 2, 275), precio, font=fnt(64), fill=rgb(BLANCO), anchor="mm")

    # Incluye
    y = 370
    for item in slide.get("incluye", []):
        lineas = wrap(f"✓  {item}", fnt(38, bold=False), W - 160)
        for linea in lineas:
            draw.text((80, y), linea, font=fnt(38, bold=False), fill=rgb(BLANCO))
            y += 52
        y += 10

    return footer_bar(img)


def render_cta(bg: Image.Image, slide: dict) -> Image.Image:
    """Slide final de llamada a la acción."""
    img = overlay(bg, opacity=140)

    logo_size = 170
    logo_path = Path("assets/logo_petcolinas.png")
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        img.paste(logo, ((W - logo_size) // 2, 130), logo)

    draw = ImageDraw.Draw(img)

    titulo = slide.get("titulo", "¡Agenda tu cita!")
    y = 350
    for line in wrap(titulo, fnt(72), W - 120):
        draw.text((W // 2, y), line, font=fnt(72), fill=rgb(BLANCO),
                  anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0, 200))
        y += 88

    sub = slide.get("subtitulo", "")
    if sub:
        draw.text((W // 2, y + 15), sub, font=fnt(42, bold=False),
                  fill=rgb(DORADO), anchor="mm")
        y += 65

    for linea in slide.get("lineas", []):
        draw.text((W // 2, y + 10), linea, font=fnt(36, bold=False),
                  fill=rgb(BLANCO), anchor="mm")
        y += 52

    banda = Image.new("RGBA", (W, 8), rgb(NARANJA))
    img.paste(banda, (0, H - 80), banda)

    return footer_bar(img)


RENDERERS = {
    "portada":   render_portada,
    "contenido": render_contenido,
    "dos_col":   render_dos_col,
    "precio":    render_precio,
    "cta":       render_cta,
}

# ── Orquestador principal ─────────────────────────────────────────────────────
def main():
    config_path = Path("carrusel_config.json")
    if not config_path.exists():
        print("ERROR: No existe carrusel_config.json")
        print("Crea ese archivo con la definición del carrusel. Ver README o ejemplos.")
        sys.exit(1)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    folder  = config["folder"]
    slides  = config["slides"]
    caption = config.get("caption", "")
    fast    = config.get("fast_model", False)

    out_dir = Path("posts") / folder
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"{'[DRY-RUN] ' if _DRY_RUN else ''}Generando carrusel '{folder}' — {len(slides)} slides")
    print()

    for i, slide in enumerate(slides, 1):
        tipo   = slide.get("tipo", "contenido")
        prompt = slide.get("bg_prompt", "Beautiful professional pet care photography, warm lighting")

        print(f"  Slide {i}/{len(slides)} [{tipo}]  {prompt[:65]}...")

        bg = generate_bg(prompt, fast=fast)

        renderer = RENDERERS.get(tipo, render_contenido)
        result   = renderer(bg, slide)
        result   = result.convert("RGB")

        out_path = out_dir / f"slide_{i:02d}.png"
        result.save(str(out_path), "PNG")
        print(f"    ✓ {out_path}")

        # Respeta rate limit del tier gratuito (~2 req/min)
        if i < len(slides) and not _DRY_RUN:
            wait = 35 if not fast else 15
            print(f"    ⏳ Esperando {wait}s (rate limit)...")
            time.sleep(wait)

    # caption.txt
    (out_dir / "caption.txt").write_text(caption, encoding="utf-8")
    print(f"  ✓ caption.txt")

    print()
    print(f"✅  Listo → posts/{folder}/  ({len(slides)} imágenes)")
    if not _DRY_RUN:
        print()
        print("   Siguiente paso:")
        print("     git add posts/" + folder + " && git commit -m 'carrusel: " + folder + "'")
        print("     # Actualizar publish.json para publicar en Instagram")


if __name__ == "__main__":
    main()
