#!/usr/bin/env python3
"""
bridge_afiche.py — Renderiza un AFICHE de marca PetColinas (lado servidor).

Se invoca desde bridge_generate.py cuando el pedido trae "type": "afiche".
Genera un fondo con Imagen 4 y superpone la marca PetColinas (logo real,
colores, bandas de texto). El texto se dibuja con Pillow, asi que sale
EXACTO (sin errores de IA).

Campos del pedido (image_requests/pending.json):
  type      = "afiche"
  titulo    (obligatorio)   titular grande
  subtitulo (opcional)      linea dorada bajo el titulo
  puntos    (opcional)      lista de vinetas
  cta       (opcional)      texto de la barra naranja (ej "WhatsApp: 809-...")
  footer    (opcional)      pie (default: marca + IG)
  bg_prompt (opcional)      descripcion del fondo (default generico de marca)

La API key se lee del entorno (GOOGLE_AI_KEY) y NUNCA se imprime.
"""

import base64
import os
import sys
import time
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1080

# Colores de marca PetColinas
VERDE = "#1a6b3a"
VERDE_DARK = "#145230"
NARANJA = "#d45f1e"
DORADO = "#c9a227"
BLANCO = "#ffffff"

LOGO_PATH = Path("assets/logo_petcolinas.png")
FOOTER_DEFAULT = "PetColinas  ·  Plaza Las Colinas, SDO Oeste  ·  @petcolinasrd"

_FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
_BOLD = str(_FONT_DIR / "DejaVuSans-Bold.ttf")
_REG = str(_FONT_DIR / "DejaVuSans.ttf")


def rgb(hex_color: str, alpha: int = 255) -> tuple:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def fnt(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_BOLD if bold else _REG, size)


def wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list:
    palabras, lineas, cur = text.split(), [], []
    for w in palabras:
        if font.getlength(" ".join(cur + [w])) <= max_w:
            cur.append(w)
        else:
            if cur:
                lineas.append(" ".join(cur))
            cur = [w]
    if cur:
        lineas.append(" ".join(cur))
    return lineas


def generar_fondo(prompt: str, key: str) -> Image.Image:
    import requests

    url = "https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict"
    headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
    full = (
        f"{prompt}. Professional photography, vibrant colors, clean composition, "
        "no text, no watermarks, no overlaid captions, high quality."
    )
    payload = {
        "instances": [{"prompt": full}],
        "parameters": {"sampleCount": 1, "aspectRatio": "1:1",
                       "safetyFilterLevel": "block_only_high",
                       "personGeneration": "allow_adult"},
    }
    ultimo = ""
    for intento in range(3):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            if r.status_code == 200:
                b64 = r.json()["predictions"][0]["bytesBase64Encoded"]
                img = Image.open(BytesIO(base64.b64decode(b64))).convert("RGBA")
                return img.resize((W, H), Image.LANCZOS)
            ultimo = f"HTTP {r.status_code}"
            if r.status_code in (400, 403):
                sys.exit(f"ERROR ({ultimo}): {r.text[:300]}")
        except requests.RequestException as e:
            ultimo = type(e).__name__
        if intento < 2:
            time.sleep(6)
    # Fallback: fondo verde de marca si Imagen no responde.
    print(f"Aviso: usando fondo de marca (Imagen fallo: {ultimo})")
    base = Image.new("RGBA", (W, H), rgb(VERDE_DARK))
    d = ImageDraw.Draw(base)
    for i in range(0, W, 60):
        d.line([(i, 0), (i, H)], fill=rgb(VERDE, 30), width=1)
        d.line([(0, i), (W, i)], fill=rgb(VERDE, 30), width=1)
    return base


def overlay(img: Image.Image, opacity: int = 150) -> Image.Image:
    capa = Image.new("RGBA", img.size, (0, 0, 0, opacity))
    return Image.alpha_composite(img.convert("RGBA"), capa)


def logo_box(img: Image.Image) -> None:
    """Logo en una caja blanca redondeada arriba a la izquierda."""
    if not LOGO_PATH.exists():
        return
    d = ImageDraw.Draw(img)
    bx, by, bs = 30, 30, 180
    d.rounded_rectangle([bx, by, bx + bs, by + bs], radius=24, fill=rgb(BLANCO))
    logo = Image.open(LOGO_PATH).convert("RGBA").resize((bs - 24, bs - 24), Image.LANCZOS)
    img.paste(logo, (bx + 12, by + 12), logo)


def render(req: dict, out_dir: Path, key: str) -> None:
    titulo = str(req.get("titulo", "")).strip()
    if not titulo:
        sys.exit("ERROR: un afiche necesita 'titulo'.")
    subtitulo = str(req.get("subtitulo", "")).strip()
    puntos = [str(p).strip() for p in req.get("puntos", []) if str(p).strip()]
    cta = str(req.get("cta", "")).strip()
    footer = str(req.get("footer", "") or FOOTER_DEFAULT).strip()
    bg_prompt = str(req.get("bg_prompt", "")).strip() or \
        "Bright modern veterinary clinic with a happy healthy dog and cat, warm natural light"

    bg = generar_fondo(bg_prompt, key)
    img = overlay(bg, 150)
    logo_box(img)
    d = ImageDraw.Draw(img)

    # Titulo (banda verde redondeada, texto blanco)
    y = 250
    lineas = wrap(titulo.upper(), fnt(70), W - 160)
    alto_banda = 40 + len(lineas) * 82
    d.rounded_rectangle([40, y - 20, W - 40, y - 20 + alto_banda], radius=28, fill=rgb(VERDE, 235))
    yy = y + 20
    for ln in lineas:
        d.text((W // 2, yy), ln, font=fnt(70), fill=rgb(BLANCO), anchor="mm")
        yy += 82
    y = y - 20 + alto_banda + 30

    # Subtitulo dorado
    if subtitulo:
        d.text((W // 2, y), subtitulo, font=fnt(44, bold=False), fill=rgb(DORADO), anchor="mm")
        y += 70

    # Puntos
    for p in puntos:
        for ln in wrap(f"✦  {p}", fnt(40, bold=False), W - 150):
            d.text((70, y), ln, font=fnt(40, bold=False), fill=rgb(BLANCO),
                   stroke_width=1, stroke_fill=(0, 0, 0, 160))
            y += 56
        y += 12

    # CTA (barra naranja redondeada)
    if cta:
        cy = H - 250
        d.rounded_rectangle([90, cy, W - 90, cy + 96], radius=48, fill=rgb(NARANJA, 240))
        d.text((W // 2, cy + 48), cta, font=fnt(46), fill=rgb(BLANCO), anchor="mm")

    # Footer
    d.rectangle([0, H - 72, W, H], fill=rgb(VERDE_DARK, 235))
    d.text((W // 2, H - 36), footer, font=fnt(24, bold=False), fill=rgb(BLANCO), anchor="mm")

    out_dir.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(str(out_dir / "image.png"), "PNG")
    print(f"OK: afiche renderizado en {out_dir}/image.png")


if __name__ == "__main__":
    # Permite pruebas locales: python bridge_afiche.py (lee pending.json)
    import json
    req = json.loads(Path("image_requests/pending.json").read_text(encoding="utf-8"))
    render(req, Path("image_requests/output") / req["id"], os.environ.get("GOOGLE_AI_KEY", ""))
