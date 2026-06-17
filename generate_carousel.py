"""
Genera slides de carrusel para PetColinas usando Pillow.
Uso: python generate_carousel.py <nombre_carpeta>
Salida: posts/<nombre_carpeta>/01.png … XX.png
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# ── Colores de marca ────────────────────────────────────────────────────────
VERDE      = "#1a6b3a"
VERDE_DARK = "#145230"
NARANJA    = "#d45f1e"
DORADO     = "#c9a227"
CREMA      = "#fdf8f0"
BLANCO     = "#ffffff"
GRIS_SUAVE = "#f0ede8"
GRIS_TEXT  = "#555555"
NEGRO_SUAVE= "#1a1a1a"

# ── Fuentes ─────────────────────────────────────────────────────────────────
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

SIZE = 1080  # cuadrado 1080×1080

def font(size, bold=False):
    path = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(path, size)

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def new_canvas(bg):
    img = Image.new("RGB", (SIZE, SIZE), hex_to_rgb(bg))
    return img, ImageDraw.Draw(img)

def add_logo(img, size=130, pos="top-right", margin=40):
    logo_path = "assets/logo_petcolinas.png"
    if not os.path.exists(logo_path):
        return
    logo = Image.open(logo_path).convert("RGBA")
    ratio = size / logo.width
    logo = logo.resize((size, int(logo.height * ratio)), Image.LANCZOS)
    lw, lh = logo.size
    if pos == "top-right":
        x, y = SIZE - lw - margin, margin
    elif pos == "bottom-right":
        x, y = SIZE - lw - margin, SIZE - lh - margin
    elif pos == "bottom-left":
        x, y = margin, SIZE - lh - margin
    elif pos == "center":
        x, y = (SIZE - lw) // 2, (SIZE - lh) // 2
    img.paste(logo, (x, y), logo)

def draw_rect(draw, x1, y1, x2, y2, color, radius=20):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=hex_to_rgb(color))

def draw_text_wrapped(draw, text, x, y, max_width, fnt, color, line_gap=12):
    """Dibuja texto con salto de linea automatico. Retorna Y final."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=fnt)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    cy = y
    for line in lines:
        draw.text((x, cy), line, font=fnt, fill=hex_to_rgb(color))
        bbox = draw.textbbox((0, 0), line, font=fnt)
        cy += (bbox[3] - bbox[1]) + line_gap
    return cy

def draw_centered(draw, text, y, fnt, color):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    draw.text(((SIZE - w) // 2, y), text, font=fnt, fill=hex_to_rgb(color))
    return y + (bbox[3] - bbox[1])

def accent_bar(draw, color, height=12):
    draw.rectangle([0, 0, SIZE, height], fill=hex_to_rgb(color))

def footer_bar(draw, color=VERDE, height=70):
    draw.rectangle([0, SIZE - height, SIZE, SIZE], fill=hex_to_rgb(color))

def add_footer_text(draw, text, fnt_size=26):
    fnt = font(fnt_size)
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    x = (SIZE - w) // 2
    y = SIZE - 70 + (70 - (bbox[3] - bbox[1])) // 2
    draw.text((x, y), text, font=fnt, fill=hex_to_rgb(BLANCO))

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Portada
# ════════════════════════════════════════════════════════════════════════════
def slide_01():
    img, draw = new_canvas(VERDE)

    # Circulo decorativo fondo
    draw.ellipse([-200, -200, 700, 700], fill=hex_to_rgb(VERDE_DARK))
    draw.ellipse([600, 600, 1200, 1200], fill=hex_to_rgb(VERDE_DARK))

    # Banda superior naranja
    draw_rect(draw, 0, 0, SIZE, 14, NARANJA, radius=0)

    # Chip "GUIA COMPLETA"
    draw_rect(draw, 340, 180, 740, 230, NARANJA, radius=30)
    chip_fnt = font(26, bold=True)
    chip_text = "GUIA COMPLETA"
    bbox = draw.textbbox((0,0), chip_text, font=chip_fnt)
    draw.text(((SIZE - (bbox[2]-bbox[0]))//2, 191), chip_text, font=chip_fnt, fill=hex_to_rgb(BLANCO))

    # Titulo principal
    t1_fnt = font(90, bold=True)
    draw_centered(draw, "Protege", 265, t1_fnt, BLANCO)
    draw_centered(draw, "a tu", 365, t1_fnt, DORADO)
    draw_centered(draw, "peludito", 465, t1_fnt, BLANCO)

    # Subtitulo
    sub_fnt = font(38)
    draw_centered(draw, "Todo sobre las vacunas", 590, sub_fnt, CREMA)
    draw_centered(draw, "que necesita tu perrito", 640, sub_fnt, CREMA)

    # Linea decorativa
    draw.rectangle([350, 710, 730, 716], fill=hex_to_rgb(DORADO))

    # Footer
    footer_bar(draw, VERDE_DARK, 120)
    add_footer_text(draw, "@petcolinas  |  809-752-6806", 28)

    add_logo(img, size=160, pos="bottom-right", margin=20)
    return img

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Por que vacunar
# ════════════════════════════════════════════════════════════════════════════
def slide_02():
    img, draw = new_canvas(CREMA)
    accent_bar(draw, VERDE, height=14)

    # Titulo
    t_fnt = font(62, bold=True)
    draw_centered(draw, "¿Por que vacunar", 60, t_fnt, NEGRO_SUAVE)
    draw_centered(draw, "a tu perrito?", 135, t_fnt, VERDE)

    # Linea
    draw.rectangle([140, 225, 940, 231], fill=hex_to_rgb(NARANJA))

    razones = [
        ("Previene enfermedades",  "mortales como el Parvo y el Moquillo"),
        ("Protege a toda",          "la familia, incluyendo a los ninos"),
        ("Evita contagios",         "entre mascotas en parques y paseos"),
        ("Sale mucho mas barato",   "vacunar que tratar una enfermedad"),
    ]

    y = 270
    bullet_fnt  = font(40, bold=True)
    detail_fnt  = font(33)
    icon_fnt    = font(44, bold=True)

    for i, (titulo, detalle) in enumerate(razones):
        # Tarjeta
        card_y1 = y
        card_y2 = y + 150
        bg = BLANCO if i % 2 == 0 else GRIS_SUAVE
        draw_rect(draw, 60, card_y1, SIZE - 60, card_y2, bg, radius=18)

        # Numero
        draw_rect(draw, 60, card_y1, 120, card_y2, VERDE, radius=18)
        num_text = str(i + 1)
        nb = draw.textbbox((0,0), num_text, font=icon_fnt)
        nx = 60 + (60 - (nb[2]-nb[0])) // 2
        ny = card_y1 + (150 - (nb[3]-nb[1])) // 2
        draw.text((nx, ny), num_text, font=icon_fnt, fill=hex_to_rgb(BLANCO))

        # Texto
        draw.text((145, card_y1 + 28), titulo, font=bullet_fnt, fill=hex_to_rgb(VERDE_DARK))
        draw.text((145, card_y1 + 82), detalle, font=detail_fnt, fill=hex_to_rgb(GRIS_TEXT))

        y += 162

    footer_bar(draw, VERDE, 55)
    add_footer_text(draw, "PetColinas — Veterinaria y Grooming", 24)
    add_logo(img, size=90, pos="top-right", margin=20)
    return img

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Vacunas disponibles y precios
# ════════════════════════════════════════════════════════════════════════════
def slide_03():
    img, draw = new_canvas(BLANCO)
    accent_bar(draw, NARANJA, height=14)

    # Header naranja
    draw_rect(draw, 0, 14, SIZE, 200, NARANJA, radius=0)
    h_fnt = font(56, bold=True)
    draw_centered(draw, "Vacunas disponibles", 40, h_fnt, BLANCO)
    sub_fnt = font(34)
    draw_centered(draw, "en PetColinas", 115, sub_fnt, CREMA)

    vacunas = [
        ("Quintuple",     "RD$1,200",  "Parvovirus, moquillo, hepatitis,\nparainfluenza y leptospirosis"),
        ("Antirrábica",   "RD$1,500",  "Obligatoria por ley — protege\ntambien a tu familia"),
        ("Giardia",       "RD$1,450",  "Previene parasitos intestinales\nmuy comunes en RD"),
        ("Bordetella",    "RD$1,400",  "Tos de las perreras — ideal\nsi va a guarderia o parques"),
        ("Desparasitacion","RD$300",   "Albendazol — limpia parasitos\ninternos cada 3 meses"),
    ]

    y = 215
    name_fnt  = font(38, bold=True)
    price_fnt = font(38, bold=True)
    desc_fnt  = font(27)

    for i, (nombre, precio, desc) in enumerate(vacunas):
        bg = CREMA if i % 2 == 0 else GRIS_SUAVE
        draw_rect(draw, 40, y, SIZE - 40, y + 143, bg, radius=16)

        # Punto de color
        dot_color = VERDE if i % 2 == 0 else NARANJA
        draw.ellipse([52, y+50, 78, y+76], fill=hex_to_rgb(dot_color))

        # Nombre
        draw.text((98, y + 14), nombre, font=name_fnt, fill=hex_to_rgb(NEGRO_SUAVE))

        # Precio (derecha)
        pb = draw.textbbox((0,0), precio, font=price_fnt)
        px = SIZE - 40 - (pb[2]-pb[0]) - 20
        draw.text((px, y + 14), precio, font=price_fnt, fill=hex_to_rgb(VERDE))

        # Descripcion
        for li, line in enumerate(desc.split("\n")):
            draw.text((98, y + 68 + li*34), line, font=desc_fnt, fill=hex_to_rgb(GRIS_TEXT))

        y += 155

    footer_bar(draw, VERDE, 55)
    add_footer_text(draw, "Precios sujetos a cambio — consulta disponibilidad", 22)
    add_logo(img, size=80, pos="top-right", margin=15)
    return img

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Calendario de vacunacion
# ════════════════════════════════════════════════════════════════════════════
def slide_04():
    img, draw = new_canvas(CREMA)
    accent_bar(draw, VERDE, 14)

    t_fnt = font(58, bold=True)
    draw_centered(draw, "Calendario de", 50, t_fnt, NEGRO_SUAVE)
    draw_centered(draw, "vacunacion", 120, t_fnt, VERDE)
    draw.rectangle([200, 200, 880, 207], fill=hex_to_rgb(DORADO))

    etapas = [
        ("6 - 8 semanas",  "Primera dosis de la Quintuple"),
        ("10 - 12 semanas", "Segunda dosis + Bordetella"),
        ("14 - 16 semanas", "Tercera dosis + Antirrábica"),
        ("Cada año",        "Refuerzo anual de todas las vacunas"),
        ("Cada 3 meses",    "Desparasitacion interna (Albendazol)"),
    ]

    y = 230
    label_fnt = font(36, bold=True)
    text_fnt  = font(34)

    for i, (edad, texto) in enumerate(etapas):
        # Linea conectora
        if i < len(etapas) - 1:
            draw.rectangle([95, y + 54, 107, y + 170], fill=hex_to_rgb(VERDE if i%2==0 else NARANJA))

        # Circulo timeline
        dot_color = VERDE if i % 2 == 0 else NARANJA
        draw.ellipse([70, y + 18, 132, y + 80], fill=hex_to_rgb(dot_color))
        age_b = draw.textbbox((0,0), str(i+1), font=font(28, bold=True))
        draw.text((101-(age_b[2]-age_b[0])//2, y+25), str(i+1), font=font(28, bold=True), fill=hex_to_rgb(BLANCO))

        # Tarjeta
        draw_rect(draw, 155, y, SIZE - 50, y + 98, BLANCO, radius=16)
        draw.text((180, y + 8),  edad,  font=label_fnt, fill=hex_to_rgb(NEGRO_SUAVE))
        draw.text((180, y + 52), texto, font=text_fnt,  fill=hex_to_rgb(GRIS_TEXT))

        y += 152

    footer_bar(draw, VERDE, 55)
    add_footer_text(draw, "Tu vet te indicara el calendario exacto", 24)
    add_logo(img, size=85, pos="top-right", margin=16)
    return img

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — Señales de alerta
# ════════════════════════════════════════════════════════════════════════════
def slide_05():
    img, draw = new_canvas(BLANCO)
    accent_bar(draw, DORADO, 14)

    draw_rect(draw, 0, 14, SIZE, 195, VERDE, radius=0)
    h_fnt = font(54, bold=True)
    draw_centered(draw, "Señales de que tu", 35, h_fnt, BLANCO)
    draw_centered(draw, "perrito necesita la vet", 100, h_fnt, DORADO)

    alertas = [
        "Perdida de apetito o peso repentino",
        "Vomitos o diarrea por mas de un dia",
        "Tos persistente o dificultad al respirar",
        "Letargo, no quiere jugar ni moverse",
        "Secrecion en ojos, nariz o boca",
        "No tiene las vacunas al dia",
    ]

    y = 215
    a_fnt = font(35)
    em_fnt = font(38, bold=True)

    for i, alerta in enumerate(alertas):
        bg = CREMA if i % 2 == 0 else GRIS_SUAVE
        draw_rect(draw, 50, y, SIZE - 50, y + 100, bg, radius=14)

        # Exclamacion o check
        sym = "!" if i < 5 else "+"
        sym_color = NARANJA if i < 5 else VERDE
        draw_rect(draw, 50, y, 110, y + 100, sym_color, radius=14)
        sb = draw.textbbox((0,0), sym, font=em_fnt)
        draw.text((80-(sb[2]-sb[0])//2, y+30), sym, font=em_fnt, fill=hex_to_rgb(BLANCO))

        draw_text_wrapped(draw, alerta, 128, y + 28, 830, a_fnt, NEGRO_SUAVE, line_gap=6)
        y += 112

    footer_bar(draw, VERDE, 55)
    add_footer_text(draw, "Consultas: 809-752-6806  |  @petcolinas", 24)
    add_logo(img, size=80, pos="top-right", margin=14)
    return img

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — CTA final
# ════════════════════════════════════════════════════════════════════════════
def slide_06():
    img, draw = new_canvas(VERDE)

    # Circulo decorativo
    draw.ellipse([700, -150, 1250, 400], fill=hex_to_rgb(VERDE_DARK))
    draw.ellipse([-150, 700, 350, 1250], fill=hex_to_rgb(VERDE_DARK))

    accent_bar(draw, NARANJA, 14)

    # Logo grande centrado
    add_logo(img, size=240, pos="center")

    # Texto encima del logo
    top_fnt = font(52, bold=True)
    draw_centered(draw, "Agenda tu cita hoy", 130, top_fnt, BLANCO)
    draw_centered(draw, "y mantén a tu peludito", 195, top_fnt, CREMA)
    draw_centered(draw, "protegido todo el año", 260, top_fnt, DORADO)

    # Linea
    draw.rectangle([250, 335, 830, 341], fill=hex_to_rgb(DORADO))

    # Info de contacto (debajo del logo)
    info_items = [
        ("WhatsApp / Llamadas:", "809-752-6806"),
        ("Instagram:",           "@petcolinas"),
        ("Ubicacion:",           "Plaza Las Colinas, SDO"),
        ("Horario:",             "Todos los dias excepto martes"),
    ]

    y = 740
    label_fnt = font(30)
    value_fnt = font(30, bold=True)

    for label, value in info_items:
        lb = draw.textbbox((0,0), label + "  " + value, font=label_fnt)
        total_w = draw.textbbox((0,0), label, font=label_fnt)[2] + 10 + draw.textbbox((0,0), value, font=value_fnt)[2]
        start_x = (SIZE - total_w) // 2
        draw.text((start_x, y), label, font=label_fnt, fill=hex_to_rgb(CREMA))
        lw = draw.textbbox((0,0), label, font=label_fnt)[2]
        draw.text((start_x + lw + 10, y), value, font=value_fnt, fill=hex_to_rgb(DORADO))
        y += 52

    return img

# ════════════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════════════
def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "posts/vacunas"
    os.makedirs(folder, exist_ok=True)

    slides = [
        ("01", slide_01),
        ("02", slide_02),
        ("03", slide_03),
        ("04", slide_04),
        ("05", slide_05),
        ("06", slide_06),
    ]

    for name, fn in slides:
        path = os.path.join(folder, f"{name}.png")
        print(f"  Generando {path}...")
        img = fn()
        img.save(path, format="PNG", optimize=True)
        print(f"    -> guardado ({os.path.getsize(path)//1024} KB)")

    print(f"\nCarrusel listo en {folder}/ ({len(slides)} slides)")

if __name__ == "__main__":
    main()
