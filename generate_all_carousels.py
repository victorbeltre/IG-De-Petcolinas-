"""
Generador masivo de carruseles para PetColinas.
Genera todos los posts del calendario en posts/<carpeta>/ de una vez.
Uso: python generate_all_carousels.py
"""

import os
import json
import textwrap
from PIL import Image, ImageDraw, ImageFont

# ── Colores ──────────────────────────────────────────────────────────────────
VERDE      = "#1a6b3a"
VERDE_DARK = "#145230"
NARANJA    = "#d45f1e"
DORADO     = "#c9a227"
CREMA      = "#fdf8f0"
BLANCO     = "#ffffff"
GRIS       = "#f0ede8"
GRIS_TEXT  = "#555555"
NEGRO      = "#1a1a1a"

FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SIZE   = 1080

def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def fnt(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)

def canvas(bg=BLANCO):
    img = Image.new("RGB", (SIZE, SIZE), rgb(bg))
    return img, ImageDraw.Draw(img)

def logo(img, size=100, pos="tr", margin=28):
    p = "assets/logo_petcolinas.png"
    if not os.path.exists(p): return
    L = Image.open(p).convert("RGBA")
    r = size / L.width
    L = L.resize((size, int(L.height * r)), Image.LANCZOS)
    lw, lh = L.size
    positions = {
        "tr": (SIZE - lw - margin, margin),
        "br": (SIZE - lw - margin, SIZE - lh - margin),
        "bl": (margin, SIZE - lh - margin),
        "c":  ((SIZE - lw) // 2, (SIZE - lh) // 2),
    }
    img.paste(L, positions[pos], L)

def rrect(d, x1, y1, x2, y2, color, r=18):
    d.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=rgb(color))

def center_text(d, text, y, f, color):
    bb = d.textbbox((0, 0), text, font=f)
    w = bb[2] - bb[0]
    d.text(((SIZE - w) // 2, y), text, font=f, fill=rgb(color))
    return y + (bb[3] - bb[1])

def wrap_text(d, text, x, y, max_w, f, color, gap=10):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textbbox((0,0), t, font=f)[2] <= max_w:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    for line in lines:
        d.text((x, y), line, font=f, fill=rgb(color))
        y += d.textbbox((0,0), line, font=f)[3] + gap
    return y

def footer(d, img, text, color=VERDE, h=62, logo_pos="br"):
    d.rectangle([0, SIZE-h, SIZE, SIZE], fill=rgb(color))
    f = fnt(24)
    bb = d.textbbox((0,0), text, font=f)
    tw = bb[2]-bb[0]
    ty = SIZE - h + (h - (bb[3]-bb[1])) // 2
    d.text(((SIZE-tw)//2, ty), text, font=f, fill=rgb(BLANCO))
    if logo_pos:
        logo(img, size=80, pos=logo_pos, margin=14)

def accent(d, color=VERDE, h=14):
    d.rectangle([0, 0, SIZE, h], fill=rgb(color))

# ════════════════════════════════════════════════════════════════════════════
# PLANTILLAS DE SLIDES
# ════════════════════════════════════════════════════════════════════════════

def slide_portada(tag, title_lines, subtitle, accent_color=NARANJA):
    """Portada: fondo verde oscuro, chip tag, título grande, subtítulo."""
    img, d = canvas(VERDE)
    d.ellipse([-200,-200,600,600], fill=rgb(VERDE_DARK))
    d.ellipse([700,700,1280,1280], fill=rgb(VERDE_DARK))
    d.rectangle([0,0,SIZE,14], fill=rgb(accent_color))

    # Chip
    cf = fnt(26, True)
    cbb = d.textbbox((0,0), tag, font=cf)
    cw = cbb[2]-cbb[0]+60
    rrect(d, (SIZE-cw)//2, 175, (SIZE+cw)//2, 225, accent_color, r=30)
    d.text(((SIZE - (cbb[2]-cbb[0]))//2, 183), tag, font=cf, fill=rgb(BLANCO))

    y = 255
    tf = fnt(88, True)
    for i, line in enumerate(title_lines):
        col = DORADO if i == 1 else BLANCO
        y = center_text(d, line, y, tf, col) + 8

    sf = fnt(38)
    y += 20
    center_text(d, subtitle, y, sf, CREMA)
    d.rectangle([340, y+60, 740, y+66], fill=rgb(DORADO))

    # Footer
    d.rectangle([0, SIZE-110, SIZE, SIZE], fill=rgb(VERDE_DARK))
    ff = fnt(26)
    ft = "@petcolinas  |  809-752-6806"
    bb = d.textbbox((0,0), ft, font=ff)
    d.text(((SIZE-(bb[2]-bb[0]))//2, SIZE-110+(110-(bb[3]-bb[1]))//2), ft, font=ff, fill=rgb(BLANCO))
    logo(img, size=150, pos="br", margin=16)
    return img

def slide_lista(title, subtitle_color, items, bg=CREMA):
    """Lista numerada con tarjetas. items = [(titulo, detalle), ...]"""
    img, d = canvas(bg)
    accent(d, VERDE)

    tf = fnt(58, True)
    y = 55
    for i, part in enumerate(title.split("\n")):
        col = subtitle_color if i == 1 else NEGRO
        y = center_text(d, part, y, tf, col) + 5
    d.rectangle([140, y+10, 940, y+16], fill=rgb(NARANJA))
    y += 38

    bf = fnt(38, True)
    df = fnt(32)
    nf = fnt(42, True)

    for i, (t, det) in enumerate(items):
        cy1, cy2 = y, y+148
        rrect(d, 60, cy1, SIZE-60, cy2, BLANCO if i%2==0 else GRIS)
        rrect(d, 60, cy1, 120, cy2, VERDE if i%2==0 else NARANJA)
        nb = d.textbbox((0,0), str(i+1), font=nf)
        d.text((90-(nb[2]-nb[0])//2, cy1+(148-(nb[3]-nb[1]))//2), str(i+1), font=nf, fill=rgb(BLANCO))
        d.text((138, cy1+22), t, font=bf, fill=rgb(VERDE_DARK))
        d.text((138, cy1+76), det, font=df, fill=rgb(GRIS_TEXT))
        y += 160

    footer(d, img, "PetColinas — Veterinaria y Grooming")
    return img

def slide_precios(header_title, header_sub, items):
    """Tabla de precios. items = [(nombre, precio, descripcion), ...]"""
    img, d = canvas(BLANCO)
    accent(d, NARANJA)
    d.rectangle([0,14,SIZE,195], fill=rgb(NARANJA))
    center_text(d, header_title, 40, fnt(54,True), BLANCO)
    center_text(d, header_sub, 112, fnt(34), CREMA)

    nf = fnt(38, True)
    pf = fnt(38, True)
    df = fnt(27)

    y = 210
    for i, (nombre, precio, desc) in enumerate(items):
        bg_c = CREMA if i%2==0 else GRIS
        card_h = 148 if "\n" not in desc else 168
        rrect(d, 40, y, SIZE-40, y+card_h, bg_c)
        dc = VERDE if i%2==0 else NARANJA
        d.ellipse([52, y+card_h//2-14, 80, y+card_h//2+14], fill=rgb(dc))
        d.text((98, y+14), nombre, font=nf, fill=rgb(NEGRO))
        pb = d.textbbox((0,0), precio, font=pf)
        d.text((SIZE-40-(pb[2]-pb[0])-16, y+14), precio, font=pf, fill=rgb(VERDE))
        for li, line in enumerate(desc.split("\n")):
            d.text((98, y+68+li*36), line, font=df, fill=rgb(GRIS_TEXT))
        y += card_h + 10

    footer(d, img, "Precios sujetos a cambio — consulta disponibilidad")
    return img

def slide_timeline(title, title2_color, steps):
    """Timeline vertical. steps = [(etiqueta, descripcion), ...]"""
    img, d = canvas(CREMA)
    accent(d, VERDE)
    center_text(d, title, 55, fnt(58,True), NEGRO)
    y0 = center_text(d, "", 125, fnt(58,True), NEGRO)  # dummy
    center_text(d, title, 55, fnt(58,True), NEGRO)
    t2_y = 55 + d.textbbox((0,0), title, font=fnt(58,True))[3] - d.textbbox((0,0), title, font=fnt(58,True))[1] + 8

    # draw second title line in color
    parts = title.split("|")
    if len(parts) == 2:
        img2, d2 = canvas(CREMA)
        accent(d2, VERDE)
        center_text(d2, parts[0].strip(), 55, fnt(58,True), NEGRO)
        y_line2 = 55 + fnt(58,True).getbbox(parts[0].strip())[3] + 8
        center_text(d2, parts[1].strip(), y_line2, fnt(58,True), title2_color)
        d2.rectangle([200, y_line2+68, 880, y_line2+74], fill=rgb(DORADO))
        img, d = img2, d2
        y_start = y_line2 + 100
    else:
        d.rectangle([200, 200, 880, 206], fill=rgb(DORADO))
        y_start = 235

    lf = fnt(36,True)
    tf2 = fnt(32)
    nf = fnt(28,True)

    y = y_start
    for i, (lbl, desc) in enumerate(steps):
        if i < len(steps)-1:
            dc = VERDE if i%2==0 else NARANJA
            d.rectangle([95, y+54, 107, y+190], fill=rgb(dc))
        dot_c = VERDE if i%2==0 else NARANJA
        d.ellipse([70, y+18, 132, y+80], fill=rgb(dot_c))
        nb = d.textbbox((0,0), str(i+1), font=nf)
        d.text((101-(nb[2]-nb[0])//2, y+25), str(i+1), font=nf, fill=rgb(BLANCO))
        rrect(d, 155, y, SIZE-50, y+98, BLANCO)
        d.text((180, y+8),  lbl,  font=lf, fill=rgb(NEGRO))
        d.text((180, y+52), desc, font=tf2, fill=rgb(GRIS_TEXT))
        y += 158

    footer(d, img, "Tu vet te orientara en cada etapa")
    return img

def slide_tips(title, tip_color, tips, bg=BLANCO):
    """Tips en tarjetas horizontales. tips = [(simbolo, texto), ...]"""
    img, d = canvas(bg)
    d.rectangle([0,0,SIZE,195], fill=rgb(VERDE))
    accent(d, DORADO)
    center_text(d, title.split("\n")[0], 38, fnt(52,True), BLANCO)
    if "\n" in title:
        center_text(d, title.split("\n")[1], 102, fnt(52,True), DORADO)

    sf = fnt(38, True)
    tf2 = fnt(33)

    y = 210
    for i, (sym, text) in enumerate(tips):
        bg_c = CREMA if i%2==0 else GRIS
        rrect(d, 50, y, SIZE-50, y+105, bg_c)
        rrect(d, 50, y, 112, y+105, tip_color)
        sb = d.textbbox((0,0), sym, font=sf)
        d.text((81-(sb[2]-sb[0])//2, y+(105-(sb[3]-sb[1]))//2), sym, font=sf, fill=rgb(BLANCO))
        wrap_text(d, text, 130, y+28, 870, tf2, NEGRO, gap=6)
        y += 117

    footer(d, img, "Consultas: 809-752-6806  |  @petcolinas")
    return img

def slide_comparacion(title, left_title, left_items, right_title, right_items, left_color=VERDE, right_color=NARANJA):
    """Dos columnas comparativas."""
    img, d = canvas(CREMA)
    accent(d, VERDE)
    center_text(d, title, 55, fnt(54,True), NEGRO)
    d.rectangle([140, 130, 940, 136], fill=rgb(DORADO))

    col_w = 460
    lx, rx = 50, SIZE//2 + 30

    for x, col_title, items, col in [(lx, left_title, left_items, left_color), (rx, right_title, right_items, right_color)]:
        rrect(d, x, 155, x+col_w, 220, col)
        ttb = d.textbbox((0,0), col_title, font=fnt(32,True))
        tw = ttb[2]-ttb[0]
        d.text((x + (col_w-tw)//2, 165), col_title, font=fnt(32,True), fill=rgb(BLANCO))

        y = 238
        for item in items:
            rrect(d, x, y, x+col_w, y+110, BLANCO)
            d.ellipse([x+14, y+40, x+38, y+64], fill=rgb(col))
            wrap_text(d, item, x+52, y+20, col_w-65, fnt(28), NEGRO, gap=4)
            y += 122

    footer(d, img, "Pregunta por nuestros planes en 809-752-6806")
    return img

def slide_cta():
    """CTA final con logo grande y datos de contacto."""
    img, d = canvas(VERDE)
    d.ellipse([650,-100,1200,450], fill=rgb(VERDE_DARK))
    d.ellipse([-120,680,350,1200], fill=rgb(VERDE_DARK))
    d.rectangle([0,0,SIZE,14], fill=rgb(NARANJA))

    center_text(d, "Agenda tu cita hoy", 130, fnt(52,True), BLANCO)
    center_text(d, "y dale lo mejor", 195, fnt(52,True), CREMA)
    center_text(d, "a tu peludito", 260, fnt(52,True), DORADO)
    d.rectangle([260,335,820,341], fill=rgb(DORADO))

    logo(img, size=230, pos="c")

    info = [
        ("WhatsApp / Llamadas:", "809-752-6806"),
        ("Instagram:", "@petcolinas"),
        ("Ubicacion:", "Plaza Las Colinas, SDO"),
        ("Horario:", "Todos los dias excepto martes"),
    ]
    y = 745
    lf, vf = fnt(29), fnt(29,True)
    for lbl, val in info:
        lb = d.textbbox((0,0), lbl, font=lf)
        vb = d.textbbox((0,0), val,  font=vf)
        total = (lb[2]-lb[0]) + 12 + (vb[2]-vb[0])
        sx = (SIZE-total)//2
        d.text((sx, y), lbl, font=lf, fill=rgb(CREMA))
        d.text((sx + (lb[2]-lb[0]) + 12, y), val, font=vf, fill=rgb(DORADO))
        y += 54
    return img

# ════════════════════════════════════════════════════════════════════════════
# DEFINICION DE TODOS LOS CARRUSELES
# Formato: lista de (funcion, args)
# ════════════════════════════════════════════════════════════════════════════

CARRUSELES = {

"grooming-precios": {
    "caption": """✂️ ¿Tu peludito necesita un buen baño y corte? ¡En PetColinas tenemos el servicio perfecto para él! 🐶

Ofrecemos baños, cortes y servicios de grooming para perros de todos los tamaños — desde los más pequeñitos hasta los más grandotes — con productos de calidad y manos expertas que harán que tu mascota salga luciendo espectacular.

👉 ¡Llama o escríbenos y agenda su turno hoy!

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #GroomingRD #BanoPerros #PeluqueriaCanina #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #BanoConAmor #TuPeludito #MascotasFelices #CorteDePerros""",
    "slides": [
        ("portada", dict(tag="SERVICIOS Y PRECIOS", title_lines=["Tu peludito","merece","el mejor look"], subtitle="Grooming profesional en PetColinas")),
        ("lista", dict(title="Baños disponibles\npor tamaño", subtitle_color=VERDE, items=[
            ("Cachorro (hasta 4 meses)", "RD$699 — suave y delicado"),
            ("Pequeño (hasta 10 kg)",    "RD$799 — baño completo"),
            ("Mediano (10–25 kg)",       "RD$949 — baño completo"),
            ("Grande (más de 25 kg)",    "RD$1,149 — baño completo"),
        ])),
        ("precios", dict(header_title="Servicios adicionales", header_sub="Para el look perfecto", items=[
            ("Corte higiénico",         "RD$490",   "Patas, zona íntima y orejas"),
            ("Corte completo",          "RD$749",   "Corte a medida según la raza"),
            ("Baño medicado",           "RD$950",   "Para piel sensible o con problemas"),
            ("Baño pequeño con línea",  "RD$999",   "Baño + productos de línea premium"),
        ])),
        ("tips", dict(title="¿Cada cuánto\nbañar a tu perro?", tip_color=VERDE, tips=[
            ("1", "Perros de pelo corto — cada 6 a 8 semanas"),
            ("2", "Perros de pelo largo — cada 4 a 6 semanas"),
            ("3", "Cachorros — desde los 3 meses, con shampoo especial"),
            ("4", "Piel sensible — baño medicado según indicación vet"),
            ("5", "Siempre con shampoo canino, nunca de uso humano"),
        ])),
        ("lista", dict(title="¿Por qué elegir\nPetColinas?", subtitle_color=NARANJA, items=[
            ("Profesionales certificados", "Años de experiencia con todo tipo de razas"),
            ("Productos de calidad",       "Shampoos y acondicionadores caninos premium"),
            ("Trato con amor",             "Tu peludito es tratado como en casa"),
            ("Resultados garantizados",    "Sale limpio, feliz y oloroso a rico"),
        ])),
        ("cta", {}),
    ]
},

"membresias": {
    "caption": """💚 ¿Sabías que puedes ahorrar hasta un 15% en todos los servicios de PetColinas? 🐾

Con nuestras membresías mensuales tu peludito siempre tendrá su cita lista, turno prioritario y descuentos exclusivos en farmacia y consultas. ¡La mejor inversión para la salud y belleza de tu mascota!

👉 Pregunta por tu membresía hoy y empieza a ahorrar desde el primer mes.

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #MembresiasMascotas #AhorraConPetColinas #GroomingRD #VeterinariaRD #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #MascotasFelices #TurnoPrioritario #TurnoVIP""",
    "slides": [
        ("portada", dict(tag="MEMBRESIAS MENSUALES", title_lines=["Ahorra más,","cuida","más"], subtitle="Planes diseñados para tu peludito")),
        ("lista", dict(title="Membresía Básica\nRD$2,800/mes", subtitle_color=VERDE, items=[
            ("4 baños mensuales",         "Un baño completo cada semana"),
            ("Turno prioritario",         "Sin espera, entra antes que nadie"),
            ("10% OFF en farmacia",       "Medicamentos y productos a mejor precio"),
            ("Tranquilidad total",        "Cita asegurada cada mes sin estrés"),
        ])),
        ("lista", dict(title="Membresía Plus\nRD$4,200/mes", subtitle_color=NARANJA, items=[
            ("4 baños + 1 corte",         "Todo lo que necesita para verse perfecto"),
            ("Turno VIP exclusivo",       "Atención preferencial siempre"),
            ("15% OFF en farmacia",       "Más ahorro en cada visita"),
            ("Consulta veterinaria",      "1 consulta gratis incluida al mes"),
        ])),
        ("comparacion", dict(
            title="¿Cuál membresía es para ti?",
            left_title="BASICA — RD$2,800",
            left_items=["4 baños mensuales", "Turno prioritario", "10% OFF farmacia", "Ideal para presupuesto fijo"],
            right_title="PLUS — RD$4,200",
            right_items=["4 baños + 1 corte", "Turno VIP exclusivo", "15% OFF farmacia + consulta gratis", "El pack completo"],
        )),
        ("tips", dict(title="¿Para quién es\nla membresía?", tip_color=NARANJA, tips=[
            ("✓", "Dueños que llevan su perro más de una vez al mes"),
            ("✓", "Mascotas con pelo largo que necesitan mantenimiento"),
            ("✓", "Perros con condiciones de piel que requieren cuidado"),
            ("✓", "Quienes quieren siempre tener turno asegurado"),
            ("✓", "Los que aman ahorra sin sacrificar calidad"),
        ])),
        ("cta", {}),
    ]
},

"bano-en-casa": {
    "caption": """🚿 ¿Bañas a tu perrito en casa? Aquí van los tips que necesitas saber para hacerlo bien y sin estrés 🐶💦

Con la técnica correcta el baño en casa puede ser una experiencia positiva para tu mascota. Pero recuerda: para un resultado profesional y productos de calidad, siempre puedes contar con PetColinas.

👉 ¿Prefieres dejarlo en manos expertas? ¡Escríbenos y agenda su cita!

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #TipsPerros #BanoEnCasa #CuidaTuMascota #PerrosRD #MascotasRD #SantoDomingoOeste #GroomingRD #ConsejosMascotas #TuPeludito #MascotasFelices #BanoPerros""",
    "slides": [
        ("portada", dict(tag="TIPS Y CONSEJOS", title_lines=["Baña a tu","perrito","como un pro"], subtitle="Guía paso a paso para el baño en casa")),
        ("lista", dict(title="Antes del baño\nlo que debes tener", subtitle_color=VERDE, items=[
            ("Shampoo canino",           "Nunca uses shampoo de humanos"),
            ("Agua tibia lista",         "Ni fría ni caliente — temperatura ambiente"),
            ("Toallas secas",            "Varias — tu perro necesita secarse bien"),
            ("Cepillo adecuado",         "Según el tipo de pelo de tu raza"),
        ])),
        ("timeline", dict(title="Durante el baño|paso a paso", title2_color=VERDE, steps=[
            ("Moja completamente",       "De patas hacia arriba, evita ojos y oídos"),
            ("Aplica el shampoo",        "Masajea con suavidad todo el cuerpo"),
            ("Enjuaga muy bien",         "Sin dejar residuos — irrita la piel"),
            ("Acondiciona el pelo",      "Para pelo largo, usa acondicionador canino"),
            ("Seca con toalla",          "Frota suave — no jales el pelo"),
        ])),
        ("tips", dict(title="Después del baño\ncuidados esenciales", tip_color=VERDE, tips=[
            ("1", "Usa secadora a temperatura baja o media"),
            ("2", "Cepilla mientras secas para evitar enredos"),
            ("3", "Revisa las orejas — limpia si hay humedad"),
            ("4", "No dejes salir al sol directo hasta estar seco"),
            ("5", "Premia con un snack — refuerza lo positivo"),
        ])),
        ("lista", dict(title="¿Cuándo ir al\nprofesional?", subtitle_color=NARANJA, items=[
            ("Pelo muy enredado",        "Los nudos apretados necesitan mano experta"),
            ("Piel irritada o con granos","El baño medicado lo resuelve"),
            ("Corte de pelo necesario",  "Para el acabado perfecto según la raza"),
            ("Quieres resultado premium","En PetColinas garantizamos el look ideal"),
        ])),
        ("cta", {}),
    ]
},

"alimentacion": {
    "caption": """🥩 La salud de tu perrito empieza en el plato 🐶 ¿Sabes qué alimentos son buenos y cuáles son peligrosos para tu mascota?

Una buena alimentación es la base de una vida larga y feliz para tu peludito. Aquí te dejamos los tips más importantes — y recuerda que en PetColinas también te orientamos en todo lo que necesitas.

👉 ¿Tienes dudas sobre la alimentación de tu mascota? ¡Consúltanos!

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #AlimentacionCanina #SaludPerros #MascotasRD #PerrosRD #NutricionCanina #SantoDomingoOeste #CuidaTuMascota #TipsPerros #ConsejosMascotas #MascotasFelices #VeterinariaRD""",
    "slides": [
        ("portada", dict(tag="NUTRICION CANINA", title_lines=["La salud","empieza","en el plato"], subtitle="Todo sobre la alimentación de tu perrito")),
        ("lista", dict(title="Alimentos seguros\npara tu perro", subtitle_color=VERDE, items=[
            ("Pollo y pavo cocidos",     "Sin huesos, sin sal ni condimentos"),
            ("Arroz blanco cocido",      "Excelente para estómagos sensibles"),
            ("Zanahoria y brócoli",      "En pequeñas cantidades, crudos o cocidos"),
            ("Huevo cocido",             "Proteína de calidad, 2-3 veces por semana"),
        ])),
        ("tips", dict(title="PELIGROSOS\npara los perros", tip_color=NARANJA, tips=[
            ("!", "Chocolate — tóxico y puede ser mortal"),
            ("!", "Uvas y pasas — daño renal grave"),
            ("!", "Cebolla y ajo — destruyen glóbulos rojos"),
            ("!", "Aguacate — problemas digestivos y cardiacos"),
            ("!", "Huesos cocinados — se astillan y perforan intestinos"),
        ])),
        ("timeline", dict(title="¿Cuántas veces al|día debe comer?", title2_color=NARANJA, steps=[
            ("Cachorros (2-6 meses)",    "3 a 4 veces al día — estómagos pequeños"),
            ("Cachorros (6-12 meses)",   "2 a 3 veces al día"),
            ("Adultos (1-7 años)",       "2 veces al día — mañana y tarde"),
            ("Senior (7+ años)",         "2 veces al día, porciones más pequeñas"),
            ("Siempre agua fresca",      "Disponible las 24 horas del día"),
        ])),
        ("lista", dict(title="Señales de mala\nalimentación", subtitle_color=NARANJA, items=[
            ("Peso excesivo",            "Porciones muy grandes o comida de mesa"),
            ("Pelo opaco o con caída",   "Déficit de proteínas o vitaminas"),
            ("Diarrea frecuente",        "Alimento inadecuado o cambio brusco"),
            ("Poco apetito",             "Consulta al vet — puede ser problema de salud"),
        ])),
        ("cta", {}),
    ]
},

"primeros-auxilios": {
    "caption": """🚨 ¿Sabrías qué hacer si tu perrito tiene una emergencia? Los primeros minutos son clave 🐾

Conocer los primeros auxilios básicos para mascotas puede salvarle la vida a tu peludito. Aprende estas señales y acciones esenciales — y ante cualquier emergencia, no dudes en llamarnos.

👉 Emergencias: 809-752-6806 | PetColinas siempre disponible para ti.

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #PrimerosAuxiliosMascotas #EmergenciasVet #MascotasRD #PerrosRD #VeterinariaRD #SantoDomingoOeste #CuidaTuMascota #SaludAnimal #TipsPerros #MascotasFelices #SeguridadMascotas""",
    "slides": [
        ("portada", dict(tag="EMERGENCIAS", title_lines=["Primeros","auxilios","para tu perro"], subtitle="Lo que todo dueño debe saber", accent_color=NARANJA)),
        ("tips", dict(title="Señales de\nemergencia", tip_color=NARANJA, tips=[
            ("!", "Dificultad para respirar o jadeo excesivo"),
            ("!", "Convulsiones o movimientos incontrolables"),
            ("!", "Vómitos o diarrea con sangre"),
            ("!", "Pérdida repentina de conciencia"),
            ("!", "Hinchazón abdominal repentina y dolorosa"),
        ])),
        ("timeline", dict(title="Qué hacer ante|una emergencia", title2_color=NARANJA, steps=[
            ("Mantén la calma",          "Tu perro percibe tu estrés — respira"),
            ("Llama al vet inmediatamente","809-752-6806 — te orientamos al instante"),
            ("No le des medicamentos",   "Sin indicación vet pueden empeorar todo"),
            ("Muévelo con cuidado",      "Usa una tabla o tela rígida si no puede caminar"),
            ("Ve a la clínica rápido",   "Tiempo es vida en las emergencias"),
        ])),
        ("lista", dict(title="Cómo manejar\nheridas leves", subtitle_color=VERDE, items=[
            ("Corte pequeño",            "Limpia con agua y aplica antiséptico canino"),
            ("Espina o cuerpo extraño",  "No jales — ve al vet para extraerlo"),
            ("Quemadura leve",           "Agua fría 10 min — nunca hielo ni pasta"),
            ("Golpe o caída",            "Observa 24h — si cojea o no come, al vet"),
        ])),
        ("tips", dict(title="Kit de emergencias\npara tu mascota", tip_color=VERDE, tips=[
            ("+", "Gasas y vendas — para heridas y compresión"),
            ("+", "Antiséptico canino — nunca alcohol puro"),
            ("+", "Termómetro rectal — temperatura normal 38-39°C"),
            ("+", "Guantes de látex — protección al manipular"),
            ("+", "Número del vet siempre a mano: 809-752-6806"),
        ])),
        ("cta", {}),
    ]
},

"cuidado-dental": {
    "caption": """🦷 ¿Cuándo fue la última vez que revisaste los dientes de tu perrito? La salud dental es más importante de lo que crees 🐶

Los problemas dentales son de los más comunes en perros y pueden afectar órganos vitales si no se tratan. En PetColinas te ayudamos a mantener la sonrisa de tu peludito sana y brillante.

👉 Agenda una revisión dental con nuestro vet hoy mismo.

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #SaludDentalPerros #DientesSanos #VeterinariaRD #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #HigieneDental #MascotasFelices #TipsPerros #ConsejosMascotas""",
    "slides": [
        ("portada", dict(tag="SALUD DENTAL", title_lines=["Una sonrisa","sana es","salud total"], subtitle="Guía de cuidado dental para tu perro")),
        ("lista", dict(title="Señales de problemas\ndentales", subtitle_color=NARANJA, items=[
            ("Mal aliento intenso",      "No es normal — puede indicar infección"),
            ("Dificultad para comer",    "Dolor dental que evita masticar bien"),
            ("Encías rojas o sangrantes","Gingivitis que necesita atención"),
            ("Dientes amarillos/marrones","Sarro acumulado que causa daño"),
        ])),
        ("tips", dict(title="Cómo cuidar\nlos dientes en casa", tip_color=VERDE, tips=[
            ("1", "Cepíllale los dientes 2-3 veces por semana"),
            ("2", "Usa pasta dental canina — nunca la de humanos"),
            ("3", "Juguetes masticables de goma para limpiar"),
            ("4", "Snacks dentales — ayudan a reducir el sarro"),
            ("5", "Revisión veterinaria anual de salud dental"),
        ])),
        ("lista", dict(title="¿Por qué es tan\nimportante?", subtitle_color=VERDE, items=[
            ("Afecta el corazón",        "Bacterias dentales pueden llegar al corazón"),
            ("Afecta los riñones",       "Infecciones bucales se propagan internamente"),
            ("Dolor crónico",            "Un perro con dolor dental sufre en silencio"),
            ("Pérdida de dientes",       "El sarro no tratado destruye las encías"),
        ])),
        ("precios", dict(header_title="Servicio veterinario", header_sub="Salud dental en PetColinas", items=[
            ("Consulta + revisión dental", "RD$1,500", "Diagnóstico completo de salud bucal"),
            ("Limpieza dental profesional","Consultar",  "Eliminación de sarro bajo supervisión vet"),
            ("Extracción dental",          "Consultar",  "Cuando el diente no tiene salvación"),
        ])),
        ("cta", {}),
    ]
},

"parvo": {
    "caption": """⚠️ El Parvovirus es una de las enfermedades más peligrosas para los perros — y la buena noticia es que se PREVIENE con vacuna 💉

En República Dominicana el Parvo es muy común, especialmente en cachorros. Conoce los síntomas y protege a tu peludito antes de que sea tarde.

👉 Vacuna contra el Parvo en PetColinas: RD$1,200 (Vacuna Quíntuple)

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #Parvovirus #ParvoCanino #VacunasPerros #VeterinariaRD #MascotasRD #PerrosRD #SantoDomingoOeste #SaludAnimal #CuidaTuMascota #PrevencionCanina #MascotasFelices""",
    "slides": [
        ("portada", dict(tag="PREVENCION URGENTE", title_lines=["El Parvo:","qué es y","cómo prevenir"], subtitle="La información que puede salvar a tu perro", accent_color=NARANJA)),
        ("tips", dict(title="Síntomas del\nParvovirus", tip_color=NARANJA, tips=[
            ("!", "Vómitos frecuentes y severos"),
            ("!", "Diarrea con sangre — muy característica"),
            ("!", "Letargo extremo, sin energía para moverse"),
            ("!", "Pérdida total de apetito y agua"),
            ("!", "Fiebre alta o temperatura muy baja"),
        ])),
        ("lista", dict(title="¿Quiénes están\nen mayor riesgo?", subtitle_color=NARANJA, items=[
            ("Cachorros sin vacunar",    "El grupo más vulnerable — inmunidad baja"),
            ("Perros con vacunas vencidas","La protección se pierde con el tiempo"),
            ("Perros que van al parque", "Contacto con heces de perros infectados"),
            ("Cualquier perro no vacunado","El virus sobrevive meses en el ambiente"),
        ])),
        ("timeline", dict(title="Qué hacer si|sospechas Parvo", title2_color=NARANJA, steps=[
            ("Ve al vet INMEDIATAMENTE", "Cada hora cuenta — no esperes"),
            ("No automedicamento",       "Los remedios caseros empeoran el cuadro"),
            ("Aísla a tu perro",         "El Parvo es altamente contagioso"),
            ("Desinfecta todo",          "Cloro diluido en superficies y utensilios"),
            ("Vacuna a los demás",       "Protege a todos los perros de la casa"),
        ])),
        ("lista", dict(title="La vacuna es la\núnica protección", subtitle_color=VERDE, items=[
            ("Vacuna Quíntuple",         "Protege contra Parvo — solo RD$1,200"),
            ("3 dosis de cachorro",      "A las 6, 10 y 14 semanas de vida"),
            ("Refuerzo anual",           "Mantiene la protección toda la vida"),
            ("100% prevenible",          "No hay razón para arriesgar a tu peludito"),
        ])),
        ("cta", {}),
    ]
},

"calor-mascotas": {
    "caption": """☀️ ¡El calor en RD es bravo! Y tu peludito lo siente más que tú 🐶🌡️

Los perros no sudan como los humanos — solo jadean y regulan el calor por las patas. Sigue estos consejos para mantener a tu mascota fresca y saludable durante los meses de más calor.

👉 ¿Notas señales de golpe de calor? ¡Llámanos de inmediato!

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #CalorMascotas #VeranoPerros #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #GolpeDeCalor #HidratacionMascotas #TipsPerros #MascotasFelices #SaludAnimal""",
    "slides": [
        ("portada", dict(tag="CUIDADOS DE VERANO", title_lines=["El calor también","afecta","a tu perrito"], subtitle="Protege a tu mascota en los días de más calor")),
        ("tips", dict(title="Señales de\ngolpe de calor", tip_color=NARANJA, tips=[
            ("!", "Jadeo excesivo y respiración muy rápida"),
            ("!", "Babeo más de lo normal"),
            ("!", "Encías y lengua rojas o moradas"),
            ("!", "Debilidad, tropiezos o desmayo"),
            ("!", "Temperatura corporal sobre 40°C"),
        ])),
        ("lista", dict(title="Cómo mantenerlo\nfresco y seguro", subtitle_color=VERDE, items=[
            ("Agua fresca siempre",      "Renueva el agua varias veces al día"),
            ("Sombra obligatoria",       "Nunca al sol directo — especialmente al mediodía"),
            ("Paseos temprano o tarde",  "Antes de las 9am o después de las 5pm"),
            ("Suelo fresco",             "El asfalto quema las patas en días de calor"),
        ])),
        ("tips", dict(title="Lo que NUNCA\ndebes hacer", tip_color=NARANJA, tips=[
            ("✗", "Dejar al perro en el carro — temperatura letal en minutos"),
            ("✗", "Ejercicio intenso en horas de calor pico"),
            ("✗", "Cortar el pelo al rape — el pelo protege del sol"),
            ("✗", "Ignorar el jadeo excesivo — es una señal de alerta"),
            ("✗", "Usar hielo directo — puede causar shock térmico"),
        ])),
        ("lista", dict(title="Si sospechas\ngolpe de calor", subtitle_color=NARANJA, items=[
            ("Lleva a la sombra",        "Saca del sol inmediatamente"),
            ("Agua fresca (no helada)",  "Ofrece agua — no lo fuerces a tomar"),
            ("Paños húmedos en patas",   "Cuello, axilas e inglés para bajar temperatura"),
            ("Llama al vet urgente",     "809-752-6806 — no esperes"),
        ])),
        ("cta", {}),
    ]
},

"desparasitacion": {
    "caption": """🪱 ¿Cuándo fue la última vez que desparasitaste a tu perrito? Los parásitos internos son más comunes de lo que imaginas 🐶

En República Dominicana, la humedad y el calor hacen que los parásitos intestinales sean una amenaza constante para las mascotas. La buena noticia: la desparasitación es fácil, rápida y económica.

👉 Desparasitación (Albendazol) en PetColinas: RD$300

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #DesparasitacionCanina #ParasitosInternos #VeterinariaRD #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #SaludAnimal #AguasBlanquitas #TipsPerros #MascotasFelices""",
    "slides": [
        ("portada", dict(tag="SALUD PREVENTIVA", title_lines=["Fuera","parásitos","de tu perrito"], subtitle="Guía completa de desparasitación")),
        ("tips", dict(title="Señales de\nparásitos internos", tip_color=NARANJA, tips=[
            ("!", "Barriga hinchada — especialmente en cachorros"),
            ("!", "Pérdida de peso sin razón aparente"),
            ("!", "Pelo opaco, sin brillo ni volumen"),
            ("!", "Diarrea frecuente o heces con moco"),
            ("!", "Ver parásitos en las heces o alrededor del ano"),
        ])),
        ("timeline", dict(title="Calendario de|desparasitación", title2_color=VERDE, steps=[
            ("2 semanas de vida",        "Primera dosis — protección temprana"),
            ("Cada 2 semanas hasta 3 meses","Cachorros son muy vulnerables"),
            ("Cada 3 meses (adultos)",   "Rutina de mantenimiento preventivo"),
            ("Antes de cada vacuna",     "Desparasita siempre antes de vacunar"),
            ("Después de viajes o parques","Exposición a otros animales = riesgo"),
        ])),
        ("lista", dict(title="¿Por qué desparasitar\ncon regularidad?", subtitle_color=VERDE, items=[
            ("Protege al perro",         "Los parásitos roban nutrientes y debilitan"),
            ("Protege a tu familia",     "Algunos parásitos son zoonóticos"),
            ("Mejora la digestión",      "Sin parásitos absorbe mejor los nutrientes"),
            ("Es económico",             "RD$300 cada 3 meses — inversión mínima"),
        ])),
        ("precios", dict(header_title="Desparasitación en PetColinas", header_sub="Simple, rápido y económico", items=[
            ("Albendazol (desparasitante)", "RD$300", "Elimina parásitos internos\nen una sola dosis"),
            ("Consulta + desparasitación",  "RD$1,800","Revisión completa + tratamiento\npersonalizado"),
            ("Pack cachorro completo",      "Consultar","Vacunas + desparasitación\n+ revisión general"),
        ])),
        ("cta", {}),
    ]
},

"consulta-vet": {
    "caption": """🩺 ¿Sabes cuándo llevar a tu perrito al veterinario aunque parezca sano? La medicina preventiva salva vidas 🐶💚

Una consulta a tiempo puede detectar problemas antes de que se vuelvan graves. En PetColinas contamos con veterinarios capacitados para cuidar la salud de tu mascota.

👉 Consulta veterinaria: RD$1,500 | Agenda hoy en 809-752-6806

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #ConsultaVeterinaria #VeterinariaRD #MedicinePreventiva #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #SaludAnimal #CheckupMascota #MascotasFelices #TuVetDeConfianza""",
    "slides": [
        ("portada", dict(tag="MEDICINA PREVENTIVA", title_lines=["¿Cuándo ir","al veterinario","?"], subtitle="Señales que no debes ignorar", accent_color=NARANJA)),
        ("tips", dict(title="Señales de alerta\nIR HOY", tip_color=NARANJA, tips=[
            ("!", "Vómitos o diarrea por más de 24 horas"),
            ("!", "No come ni bebe agua en todo el día"),
            ("!", "Dificultad para respirar o tos persistente"),
            ("!", "Convulsiones, desmayo o desorientación"),
            ("!", "Heridas profundas, fracturas o golpes fuertes"),
        ])),
        ("lista", dict(title="Visitas preventivas\ncuándo y por qué", subtitle_color=VERDE, items=[
            ("Cachorros — cada mes",     "Vacunas, desparasitación y revisión de crecimiento"),
            ("Adultos — 1 vez al año",   "Chequeo general, vacunas y análisis de sangre"),
            ("Senior (+7 años) — 2/año", "Detección temprana de enfermedades crónicas"),
            ("Siempre ante cambios",     "Comportamiento, apetito, peso o energía"),
        ])),
        ("precios", dict(header_title="Servicios veterinarios", header_sub="en PetColinas", items=[
            ("Consulta veterinaria",     "RD$1,500","Diagnóstico completo de salud general"),
            ("Vacuna quíntuple",         "RD$1,200","Protección 5 enfermedades en 1 dosis"),
            ("Vacuna antirrábica",       "RD$1,500","Obligatoria y protege a tu familia"),
            ("Desparasitación",          "RD$300",  "Albendazol — cada 3 meses"),
        ])),
        ("lista", dict(title="Lo que el vet revisa\nen el chequeo", subtitle_color=VERDE, items=[
            ("Peso y condición física",  "Detecta obesidad o desnutrición"),
            ("Corazón y pulmones",       "Con estetoscopio — soplos y arritmias"),
            ("Dientes y encías",         "Sarro, gingivitis y salud bucal"),
            ("Ojos, oídos y piel",       "Infecciones, ácaros y alergias"),
        ])),
        ("cta", {}),
    ]
},

"cachorro-primeros": {
    "caption": """🐾 ¿Tienes un cachorro nuevo en casa? ¡Felicidades! Los primeros meses son los más importantes para su desarrollo 🐶💚

Un buen comienzo marca la diferencia para toda la vida de tu peludito. Vacunas, desparasitación, socialización y los primeros baños — en PetColinas te acompañamos en cada etapa.

👉 Trae a tu cachorro a conocernos — primera visita sin compromiso.

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #NuevoCachorro #CachorroRD #PrimerBano #VacunasCachorro #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #MascotasFelices #CachorroFeliz #TipsNuevoDueno""",
    "slides": [
        ("portada", dict(tag="NUEVOS DUENOS", title_lines=["Tu cachorro","llegó","¿y ahora qué?"], subtitle="Guía esencial para los primeros meses")),
        ("timeline", dict(title="Primeras semanas|en casa", title2_color=VERDE, steps=[
            ("Semana 1-2 — adaptación",  "Espacio propio, rutina de horarios y calma"),
            ("Semana 3-4 — vet urgente", "Primera consulta, desparasitación y revisión"),
            ("6-8 semanas — vacunas",    "Primera dosis de la Quíntuple en PetColinas"),
            ("3 meses — primer baño",    "Ya puede recibir su primer baño profesional"),
            ("4-6 meses — socialización","Parques y contacto con otros perros vacunados"),
        ])),
        ("lista", dict(title="Lo que necesita\nsu primer kit", subtitle_color=VERDE, items=[
            ("Cama o cojín propio",      "Espacio seguro donde se sienta protegido"),
            ("Platos de acero inoxidable","Fáciles de limpiar y sin bacterias"),
            ("Correa y collar con ID",   "Siempre con tu número de contacto"),
            ("Juguetes mordibles",       "Para la etapa de dentición — necesario"),
        ])),
        ("tips", dict(title="Primeros errores\nque debes evitar", tip_color=NARANJA, tips=[
            ("✗", "Bañarlo antes de los 3 meses — riesgo de hipotermia"),
            ("✗", "Llevarlo al parque sin vacunas completas"),
            ("✗", "Alimentarlo con comida de mesa — crea malos hábitos"),
            ("✗", "Dejarlo solo mucho tiempo — genera ansiedad"),
            ("✗", "Castigarlo físicamente — daña la confianza para siempre"),
        ])),
        ("lista", dict(title="PetColinas\npara tu cachorro", subtitle_color=VERDE, items=[
            ("Primer baño especial",     "A partir de los 3 meses — protocolo suave"),
            ("Vacunas completas",        "Quíntuple, Rabia, Bordetella y más"),
            ("Desparasitación",          "Desde las 2 semanas de vida"),
            ("Consulta de bienvenida",   "El vet lo revisa de pies a cabeza"),
        ])),
        ("cta", {}),
    ]
},

"hidratacion": {
    "caption": """💧 ¿Sabes cuánta agua necesita tu perrito cada día? La deshidratación es más peligrosa de lo que parece 🐶

En el calor de RD, mantener a tu mascota bien hidratada es una prioridad. Conoce los signos de deshidratación y cómo prevenirla antes de que sea un problema.

👉 ¿Tu perrito tiene síntomas de deshidratación? ¡Llámanos!

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #HidratacionPerros #AguaFrescaSiempre #CalorRD #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #SaludAnimal #TipsPerros #MascotasFelices #VeranoMascotas""",
    "slides": [
        ("portada", dict(tag="SALUD EN VERANO", title_lines=["Agua fresca","= vida","para tu perro"], subtitle="Guía de hidratación para tu mascota")),
        ("lista", dict(title="¿Cuánta agua\nnecesita al día?", subtitle_color=VERDE, items=[
            ("Perro pequeño (hasta 10kg)", "200-400 ml diarios (aprox. 1-2 tazas)"),
            ("Perro mediano (10-25kg)",    "500-900 ml diarios"),
            ("Perro grande (más de 25kg)", "1 a 2 litros o más según actividad"),
            ("En calor o ejercicio",       "Siempre más — aumenta hasta el doble"),
        ])),
        ("tips", dict(title="Señales de\ndeshidratación", tip_color=NARANJA, tips=[
            ("!", "Encías pegajosas o secas — revisa con el dedo"),
            ("!", "Piel que no vuelve rápido al jalar suavemente"),
            ("!", "Ojos hundidos o sin brillo"),
            ("!", "Letargo y poca energía aunque no haga calor"),
            ("!", "Orina oscura o muy poca cantidad"),
        ])),
        ("tips", dict(title="Tips para que\ntome más agua", tip_color=VERDE, tips=[
            ("✓", "Cambia el agua al menos 2 veces al día"),
            ("✓", "Usa plato de acero — el plástico retiene bacterias"),
            ("✓", "Pon varios platos en distintos lugares de la casa"),
            ("✓", "Agrega un poco de caldo de pollo sin sal — les encanta"),
            ("✓", "Plato con hielo en días de mucho calor"),
        ])),
        ("lista", dict(title="Qué hacer ante\ndeshidratación", subtitle_color=NARANJA, items=[
            ("Ofrece agua inmediatamente", "En pequeñas cantidades cada 10 minutos"),
            ("Lugar fresco y tranquilo",   "Sácalo del sol y el calor de inmediato"),
            ("Paños húmedos en patas",     "Ayuda a bajar temperatura corporal"),
            ("Si no mejora en 30 min",     "Llama al vet urgente — 809-752-6806"),
        ])),
        ("cta", {}),
    ]
},

"grooming-regular": {
    "caption": """✨ ¿Sabías que el grooming regular no es solo un tema de estética? Es SALUD para tu peludito 🐶💚

Un perro bien arreglado es un perro más saludable, más cómodo y más feliz. En PetColinas hacemos mucho más que un simple baño — cuidamos a tu mascota de cabeza a rabo.

👉 Agenda el turno de tu peludito hoy mismo.

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #GroomingRegular #BanoPerros #PeluqueriaCanina #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #BenefiiciosGrooming #MascotasFelices #SaludCanina #TuPeluditoFeliz""",
    "slides": [
        ("portada", dict(tag="MAS QUE ESTETICA", title_lines=["Grooming","regular =","perro sano"], subtitle="Los beneficios que nadie te conta")),
        ("lista", dict(title="Beneficios del\ngrooming frecuente", subtitle_color=VERDE, items=[
            ("Detecta problemas a tiempo", "Bultos, heridas, garrapatas o infecciones"),
            ("Previene enredos dolorosos", "El pelo enredado jala la piel y duele"),
            ("Piel más sana",              "Estimula circulación y elimina pelos muertos"),
            ("Menos pelo en casa",         "Muda controlada = tu sofá te lo agradece"),
        ])),
        ("timeline", dict(title="¿Cada cuánto|tiempo bañarlo?", title2_color=VERDE, steps=[
            ("Pelo corto (Bulldog, etc.)", "Cada 6-8 semanas — mantenimiento fácil"),
            ("Pelo mediano (Cocker, etc.)","Cada 4-6 semanas — sin llegar a enredos"),
            ("Pelo largo (Shih Tzu, etc.)","Cada 3-4 semanas — requiere más atención"),
            ("Cachorros",                  "Desde los 3 meses — protocolo especial"),
            ("Membresía mensual",          "La forma más cómoda de mantenerse al día"),
        ])),
        ("tips", dict(title="Qué revisamos\nen cada sesión", tip_color=VERDE, tips=[
            ("✓", "Estado de la piel — manchas, irritación o parásitos"),
            ("✓", "Orejas — limpieza y signos de infección"),
            ("✓", "Patas y uñas — longitud adecuada y estado"),
            ("✓", "Ojos — legañas y signos de irritación"),
            ("✓", "Pelaje — calidad, brillo y condición general"),
        ])),
        ("lista", dict(title="Membresías para\ngrooming frecuente", subtitle_color=NARANJA, items=[
            ("Básica — RD$2,800/mes",    "4 baños + turno prioritario + 10% OFF"),
            ("Plus — RD$4,200/mes",      "4 baños + corte + turno VIP + 15% OFF"),
            ("Sin membresía",            "Baños desde RD$699 según tamaño"),
            ("Siempre con amor",         "Tu peludito tratado como en casa"),
        ])),
        ("cta", {}),
    ]
},

"bano-medicado": {
    "caption": """🧴 ¿Tu perrito tiene la piel irritada, con hongos o eccema? El baño medicado puede ser la solución que necesita 🐶💚

No todos los baños son iguales. El baño medicado usa productos terapéuticos especiales para tratar condiciones específicas de la piel, con resultados visibles desde la primera sesión.

👉 Baño medicado en PetColinas: RD$950 | Agenda en 809-752-6806

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #BanoMedicado #PielCanina #DermatologiaCanina #MascotasRD #PerrosRD #VeterinariaRD #SantoDomingoOeste #CuidaTuMascota #AlergiaPerros #MascotasFelices #GroomingRD""",
    "slides": [
        ("portada", dict(tag="BAÑO TERAPEUTICO", title_lines=["Baño medicado","para piel","saludable"], subtitle="Cuando tu perro necesita más que un baño normal")),
        ("tips", dict(title="¿Cuándo necesita\nbaño medicado?", tip_color=NARANJA, tips=[
            ("!", "Picazón constante — se rasca sin parar"),
            ("!", "Manchas rojas, costras o peladas en la piel"),
            ("!", "Olor fuerte aunque esté recién bañado"),
            ("!", "Caspa excesiva o piel muy seca y escamosa"),
            ("!", "Granos, acné canino o pústulas en la piel"),
        ])),
        ("lista", dict(title="Condiciones que\ntrata el baño medicado", subtitle_color=VERDE, items=[
            ("Hongos (dermatofitosis)",  "Frecuentes en el calor y humedad de RD"),
            ("Sarna y ácaros",           "Shampoo especial junto con tratamiento vet"),
            ("Alergias cutáneas",        "Alivia la picazón y reduce la inflamación"),
            ("Pioderma (bacterias)",     "Infecciones bacterianas superficiales"),
        ])),
        ("timeline", dict(title="¿Cómo funciona el|baño medicado?", title2_color=VERDE, steps=[
            ("Evaluación previa",         "El técnico revisa el estado de la piel"),
            ("Shampoo terapéutico",       "Aplicado según la condición específica"),
            ("Tiempo de contacto",        "El producto actúa mientras hace efecto"),
            ("Enjuague y secado",         "Con cuidado especial en zonas afectadas"),
            ("Recomendaciones",           "Indicaciones de frecuencia y cuidados en casa"),
        ])),
        ("precios", dict(header_title="Servicios para piel", header_sub="en PetColinas", items=[
            ("Baño medicado",            "RD$950",   "Shampoo terapéutico\ncon tiempo de contacto"),
            ("Consulta dermatológica",   "RD$1,500", "Diagnóstico y plan\nde tratamiento completo"),
            ("Baño + consulta vet",      "RD$2,450", "Diagnóstico + tratamiento\nen una sola visita"),
        ])),
        ("cta", {}),
    ]
},

"mascotas-ninos": {
    "caption": """👶🐶 ¿Tienes hijos y mascotas en casa? ¡Es la combinación perfecta cuando se hace bien!

La convivencia entre perros y niños puede ser hermosa y enriquecedora para ambos. La clave está en la educación, la supervisión y en mantener a tu mascota sana y bien cuidada — eso incluye vacunas al día y baños regulares.

👉 Mantén a tu peludito sano para toda la familia con PetColinas.

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #MascotasYNinos #PerrosYNinos #FamiliaConMascotas #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #MascotasFelices #ConvivenciaSana #NinosYAnimales #TuFamiliaPetColinas""",
    "slides": [
        ("portada", dict(tag="FAMILIA CON MASCOTAS", title_lines=["Perros y niños","la combinación","perfecta"], subtitle="Guía para una convivencia sana y feliz")),
        ("lista", dict(title="Beneficios para\nlos niños", subtitle_color=VERDE, items=[
            ("Desarrollan empatía",       "Aprender a cuidar a otro ser vivo"),
            ("Más actividad física",      "Jugar con el perro = menos pantallas"),
            ("Reducen el estrés",         "Abrazar una mascota baja la presión"),
            ("Aprenden responsabilidad",  "Alimentar y cuidar un ser que depende de ellos"),
        ])),
        ("tips", dict(title="Reglas de seguridad\npara los niños", tip_color=VERDE, tips=[
            ("✓", "Nunca molestar al perro cuando come o duerme"),
            ("✓", "No jalar la cola, orejas ni patas"),
            ("✓", "Siempre con supervisión adulta hasta los 7-8 años"),
            ("✓", "Enseñarles a acercarse despacio y con calma"),
            ("✓", "Si el perro gruñe — dar espacio, no castigar"),
        ])),
        ("tips", dict(title="Cómo preparar\nal perro", tip_color=NARANJA, tips=[
            ("1", "Vacunas al día — esencial para proteger a los niños"),
            ("2", "Desparasitación regular — previene contagios"),
            ("3", "Baños frecuentes — higiene para toda la familia"),
            ("4", "Entrenamiento básico — siéntate, quieto, no saltes"),
            ("5", "Espacio propio — su cama donde nadie lo moleste"),
        ])),
        ("lista", dict(title="Salud de la mascota\nprotege a la familia", subtitle_color=VERDE, items=[
            ("Vacunas completas",         "Rabia — obligatoria, protege a los niños"),
            ("Sin parásitos internos",    "Algunos son transmisibles a humanos"),
            ("Baño regular",             "Menor exposición a alergenos y bacterias"),
            ("Control veterinario",       "Detección temprana de zoonosis"),
        ])),
        ("cta", {}),
    ]
},

"razas-pequenas": {
    "caption": """🐩 Los perritos pequeños tienen grandes necesidades de cuidado. ¿Conoces las razas más populares en PetColinas? 🐶✨

Poodles, Shih Tzu, Malteses, Chihuahuas y más — en PetColinas sabemos exactamente cómo cuidar a cada raza, desde el tipo de corte hasta las vacunas específicas que necesitan.

👉 ¿Qué raza tiene tu peludito? ¡Cuéntanos y agendamos su cita!

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #RazasPequeñas #Poodle #ShihTzu #Maltese #MascotasRD #PerrosRD #GroomingRD #SantoDomingoOeste #CuidaTuMascota #RazasDePerros #MascotasFelices""",
    "slides": [
        ("portada", dict(tag="RAZAS PEQUEÑAS", title_lines=["Los más pequeños","necesitan el","mejor cuidado"], subtitle="Razas favoritas en PetColinas")),
        ("lista", dict(title="Las razas más\npopulares que atendemos", subtitle_color=VERDE, items=[
            ("Poodle (Caniche)",          "Pelo rizado que requiere corte frecuente"),
            ("Shih Tzu",                  "Pelo largo sedoso — baño cada 3-4 semanas"),
            ("Maltés (Maltese)",          "Pelo blanco delicado — manchas con facilidad"),
            ("Chihuahua",                 "Pequeño pero con personalidad enorme"),
        ])),
        ("lista", dict(title="También atendemos\nestas razas adorables", subtitle_color=NARANJA, items=[
            ("Yorkshire Terrier",         "Pelo fino y largo — enredos frecuentes"),
            ("Bichon Frisé",              "Rizado y suave — corte específico de raza"),
            ("Pomerania",                 "Esponjoso y activo — pelo denso"),
            ("Schnauzer miniatura",       "Bigote y cejas icónicas — corte especial"),
        ])),
        ("tips", dict(title="Cuidados específicos\npelos pequeños", tip_color=VERDE, tips=[
            ("✓", "Baño cada 3-4 semanas — pelo largo se enreda rápido"),
            ("✓", "Cepillado diario en razas de pelo largo"),
            ("✓", "Corte de pelo cada 6-8 semanas para mantenimiento"),
            ("✓", "Limpieza de orejas semanal — razas pequeñas propensas"),
            ("✓", "Corte de uñas mensual — patas pequeñas son sensibles"),
        ])),
        ("precios", dict(header_title="Grooming razas pequeñas", header_sub="en PetColinas", items=[
            ("Baño perro pequeño",        "RD$799",   "Hasta 10 kg — baño completo"),
            ("Baño + corte higiénico",    "RD$1,289", "Baño + limpieza patas e íntimas"),
            ("Baño + corte completo",     "RD$1,549", "Look perfecto de pies a cabeza"),
            ("Membresía Básica",          "RD$2,800", "4 baños al mes — el más popular"),
        ])),
        ("cta", {}),
    ]
},

"corte-unas": {
    "caption": """✂️ ¿Le escuchas las uñas sonar en el piso cuando camina? ¡Es hora del corte! Las uñas largas le duelen y pueden causar problemas serios 🐶

El corte de uñas es uno de los cuidados más ignorados pero más importantes. En PetColinas lo hacemos con seguridad y sin estrés para tu mascota.

👉 Incluido en todos nuestros servicios de grooming | 809-752-6806

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #CorteDeUnas #CuidadoPatas #GroomingRD #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #MascotasFelices #TipsPerros #PatasPerrito #SaludCanina""",
    "slides": [
        ("portada", dict(tag="CUIDADO DE PATAS", title_lines=["Uñas cortas","= patas","sanas"], subtitle="Por qué el corte de uñas importa tanto")),
        ("tips", dict(title="Problemas que causan\nuñas largas", tip_color=NARANJA, tips=[
            ("!", "Dolor al caminar — cambia la postura para compensar"),
            ("!", "Problemas articulares por mala distribución del peso"),
            ("!", "Uñas que se curvan y clavan en la almohadilla"),
            ("!", "Resbalones en pisos lisos — riesgo de caídas"),
            ("!", "Arañazos en personas y muebles sin querer"),
        ])),
        ("lista", dict(title="¿Cada cuánto\ncortar las uñas?", subtitle_color=VERDE, items=[
            ("Perros activos que caminan", "Cada 6-8 semanas — el asfalto las desgasta"),
            ("Perros de interior",         "Cada 3-4 semanas — no se desgastan solas"),
            ("Perros mayores",             "Cada 3 semanas — se vuelven más frágiles"),
            ("Señal de alarma",            "Si escuchas el clic en el piso — ya es tiempo"),
        ])),
        ("tips", dict(title="¿Por qué ir al\nprofesional?", tip_color=VERDE, tips=[
            ("✓", "El groomer conoce el límite exacto sin llegar al nervio"),
            ("✓", "Cortarla muy corta duele y sangra — los pros evitan esto"),
            ("✓", "Limado posterior para bordes suaves"),
            ("✓", "Revisión de almohadillas — detecta heridas o inflamación"),
            ("✓", "Incluido en todos los servicios de baño en PetColinas"),
        ])),
        ("lista", dict(title="Qué revisamos\nen las patas", subtitle_color=VERDE, items=[
            ("Longitud de uñas",          "Corte preciso sin dañar el cuán vivo"),
            ("Almohadillas",              "Grietas, heridas o cuerpos extraños"),
            ("Pelo entre los dedos",      "Corte higiénico — evita resbalones"),
            ("Uña del pulgar (dewclaw)",  "La más olvidada — puede clavarse sola"),
        ])),
        ("cta", {}),
    ]
},

"turno-vip": {
    "caption": """👑 ¿Tu peludito merece atención de primera? Con la Membresía Plus de PetColinas tiene Turno VIP garantizado todos los meses 🐶✨

Sin espera, sin fila, atención preferencial y el pack completo de grooming + consulta veterinaria incluida. Para los que quieren lo mejor para su mascota.

👉 Pregunta por la Membresía Plus hoy: 809-752-6806

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #TurnoVIP #MembresiaPlus #AtencionPreferencial #GroomingVIP #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #MascotasFelices #LuxuryGrooming #TuPeluditoMerece""",
    "slides": [
        ("portada", dict(tag="MEMBRESIA PLUS", title_lines=["Tu peludito","merece el","trato VIP"], subtitle="Atención preferencial todo el mes")),
        ("lista", dict(title="¿Qué incluye el\nTurno VIP?", subtitle_color=DORADO, items=[
            ("Entrada preferencial",      "No esperas — entras directo al servicio"),
            ("Horario reservado",         "Tu hora es sagrada, sin interrupciones"),
            ("Atención personalizada",    "El mismo groomer aprende las preferencias"),
            ("Confirmación prioritaria",  "Recordatorio y confirmación con anticipación"),
        ])),
        ("comparacion", dict(
            title="Turno normal vs Turno VIP",
            left_title="TURNO NORMAL",
            left_items=["Lista de espera en temporada alta", "Horario según disponibilidad", "Atención compartida", "Baño desde RD$799"],
            right_title="TURNO VIP — PLUS",
            right_items=["Entrada directa sin espera", "Tu hora reservada cada mes", "Atención dedicada exclusiva", "Todo incluido en RD$4,200/mes"],
            left_color=GRIS_TEXT, right_color=DORADO,
        )),
        ("lista", dict(title="Todo lo que incluye\nla Membresía Plus", subtitle_color=NARANJA, items=[
            ("4 baños mensuales",         "Un baño completo cada semana"),
            ("1 corte de pelo",           "A medida según la raza y gusto"),
            ("Turno VIP exclusivo",       "Sin espera, siempre primero"),
            ("15% OFF en farmacia",       "El mayor descuento disponible"),
        ])),
        ("tips", dict(title="¿Para quién es el\nTurno VIP?", tip_color=VERDE, tips=[
            ("✓", "Mascotas con rutina fija de grooming mensual"),
            ("✓", "Dueños con agenda ocupada — reserva asegurada"),
            ("✓", "Perros que se estresan en esperas largas"),
            ("✓", "Quienes quieren la mejor relación calidad-precio"),
            ("✓", "Los que aman mimar a su peludito sin límites"),
        ])),
        ("cta", {}),
    ]
},

"moquillo": {
    "caption": """⚠️ El Moquillo es la segunda causa de muerte más común en perros no vacunados en RD. ¿El tuyo está protegido? 💉

Es altamente contagioso y muy difícil de tratar una vez que aparece. La única protección real es la vacuna Quíntuple — y en PetColinas la tenemos disponible hoy.

👉 Vacuna Quíntuple (incluye Moquillo): RD$1,200 en PetColinas

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #Moquillo #DistemperCanino #VacunasPerros #VeterinariaRD #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #PrevencionCanina #SaludAnimal #MascotasFelices""",
    "slides": [
        ("portada", dict(tag="ALERTA DE SALUD", title_lines=["El Moquillo:","conoce","y previene"], subtitle="La enfermedad que se previene con vacuna", accent_color=NARANJA)),
        ("tips", dict(title="Síntomas del\nMoquillo canino", tip_color=NARANJA, tips=[
            ("!", "Secreción ocular y nasal amarilla o verde"),
            ("!", "Fiebre alta y pérdida total de apetito"),
            ("!", "Tos y problemas respiratorios severos"),
            ("!", "Diarrea y vómitos persistentes"),
            ("!", "Convulsiones y tics nerviosos en etapas avanzadas"),
        ])),
        ("lista", dict(title="¿Cómo se\ncontagia?", subtitle_color=NARANJA, items=[
            ("Contacto directo",          "Nariz con nariz con perro infectado"),
            ("Ambiente contaminado",      "El virus sobrevive semanas en el entorno"),
            ("Secreciones infectadas",    "Orina, heces y fluidos respiratorios"),
            ("Sin contacto directo",      "Se puede contagiar sin tocarse — por el aire"),
        ])),
        ("lista", dict(title="¿Por qué es tan\npeligroso?", subtitle_color=NARANJA, items=[
            ("No tiene cura específica",  "Solo tratamiento de soporte — muy costoso"),
            ("Alta tasa de mortalidad",   "Hasta 50% sin tratamiento adecuado"),
            ("Daño neurológico",          "Las convulsiones pueden ser permanentes"),
            ("Afecta a todos",            "Perros de cualquier edad y raza"),
        ])),
        ("lista", dict(title="La vacuna es\nla única solución", subtitle_color=VERDE, items=[
            ("Vacuna Quíntuple",          "Protege contra Moquillo — solo RD$1,200"),
            ("Primera dosis: 6 semanas",  "Inicio temprano de la protección"),
            ("3 dosis de cachorro",       "Protocolo completo garantiza inmunidad"),
            ("Refuerzo anual",            "Mantener la protección de por vida"),
        ])),
        ("cta", {}),
    ]
},

"quienes-somos": {
    "caption": """💚 ¡Hola! Somos PetColinas — la veterinaria y peluquería canina de tu barrio en Santo Domingo Oeste 🐶🐱

Nacimos con una misión: darte el mejor cuidado para tu mascota con amor, profesionalismo y los precios más accesibles de la zona. Cada perrito que pasa por nuestras puertas es tratado como si fuera nuestro.

👉 Ven a conocernos — en Plaza Las Colinas te esperamos con los brazos abiertos.

📍 Plaza Las Colinas, Av. Prolongación 27 de Febrero, Santo Domingo Oeste
📞 WhatsApp / Llamadas: 809-752-6806
🕐 Abiertos todos los días excepto martes

#PetColinas #QuienesSomos #VeterinariaSDO #GroomingSDO #MascotasRD #PerrosRD #SantoDomingoOeste #CuidaTuMascota #MascotasFelices #TuVetDeConfianza #AmamosLasmascotas #ComunidadMascotera""",
    "slides": [
        ("portada", dict(tag="CONOCENOS", title_lines=["Somos","PetColinas","tu clínica"], subtitle="Veterinaria y Grooming en SDO")),
        ("lista", dict(title="Quiénes somos\ny qué hacemos", subtitle_color=VERDE, items=[
            ("Veterinaria completa",      "Consultas, vacunas y tratamientos"),
            ("Grooming profesional",      "Baños, cortes y tratamientos de piel"),
            ("Farmacia veterinaria",      "Medicamentos con descuento a miembros"),
            ("Membresías mensuales",      "Para cuidar más y gastar menos"),
        ])),
        ("lista", dict(title="¿Por qué elegir\nPetColinas?", subtitle_color=NARANJA, items=[
            ("Trato familiar y cálido",   "Tu mascota es tratada con amor genuino"),
            ("Profesionales certificados","Años de experiencia con todo tipo de razas"),
            ("Precios accesibles",        "Calidad sin que tengas que elegir entre precio"),
            ("Ubicación conveniente",     "En Plaza Las Colinas, fácil de llegar"),
        ])),
        ("precios", dict(header_title="Nuestros servicios", header_sub="todo lo que necesita tu mascota", items=[
            ("Grooming completo",        "Desde RD$699", "Baños para todos los tamaños"),
            ("Consulta veterinaria",     "RD$1,500",     "Diagnóstico profesional"),
            ("Vacunas",                  "Desde RD$1,200","Quíntuple, Rabia y más"),
            ("Membresías",               "Desde RD$2,800","Ahorra y garantiza citas"),
        ])),
        ("tips", dict(title="Dónde encontrarnos\ncómo llegar", tip_color=VERDE, tips=[
            ("📍", "Plaza Las Colinas, SDO — frente a la Av. 27 de Febrero"),
            ("📞", "WhatsApp y llamadas: 809-752-6806"),
            ("📱", "Instagram: @petcolinas — síguenos para tips y ofertas"),
            ("🕐", "Abiertos todos los días excepto martes"),
            ("💚", "Sin cita previa para urgencias — siempre disponibles"),
        ])),
        ("cta", {}),
    ]
},

}

# ════════════════════════════════════════════════════════════════════════════
# CALENDARIO — fecha: carpeta
# ════════════════════════════════════════════════════════════════════════════

SCHEDULE = {
    "2026-06-18": "grooming-precios",
    "2026-06-19": "membresias",
    "2026-06-20": "bano-en-casa",
    "2026-06-21": "alimentacion",
    "2026-06-22": "primeros-auxilios",
    "2026-06-23": "cuidado-dental",
    # "2026-06-24": martes — cerrado
    "2026-06-25": "parvo",
    "2026-06-26": "calor-mascotas",
    "2026-06-27": "desparasitacion",
    "2026-06-28": "consulta-vet",
    "2026-06-29": "cachorro-primeros",
    "2026-06-30": "hidratacion",
    # "2026-07-01": martes — cerrado
    "2026-07-02": "grooming-regular",
    "2026-07-03": "bano-medicado",
    "2026-07-04": "mascotas-ninos",
    "2026-07-05": "razas-pequenas",
    "2026-07-06": "corte-unas",
    "2026-07-07": "turno-vip",
    # "2026-07-08": martes — cerrado
    "2026-07-09": "moquillo",
    "2026-07-10": "quienes-somos",
}

# ════════════════════════════════════════════════════════════════════════════
# GENERACION
# ════════════════════════════════════════════════════════════════════════════

def generate_slide(tipo, kwargs):
    if tipo == "portada":
        return slide_portada(**kwargs)
    elif tipo == "lista":
        return slide_lista(**kwargs)
    elif tipo == "precios":
        return slide_precios(**kwargs)
    elif tipo == "timeline":
        return slide_timeline(**kwargs)
    elif tipo == "tips":
        return slide_tips(**kwargs)
    elif tipo == "comparacion":
        return slide_comparacion(**kwargs)
    elif tipo == "cta":
        return slide_cta()
    else:
        raise ValueError(f"Tipo de slide desconocido: {tipo}")

def generate_post(folder_name, data):
    out_dir = os.path.join("posts", folder_name)
    os.makedirs(out_dir, exist_ok=True)

    for i, (tipo, kwargs) in enumerate(data["slides"], 1):
        path = os.path.join(out_dir, f"{i:02d}.png")
        img = generate_slide(tipo, kwargs)
        img.save(path, format="PNG", optimize=True)

    caption_path = os.path.join(out_dir, "caption.txt")
    with open(caption_path, "w", encoding="utf-8") as f:
        f.write(data["caption"])

    return len(data["slides"])

def main():
    print(f"\n{'='*55}")
    print(f"  GENERADOR MASIVO DE CARRUSELES PETCOLINAS")
    print(f"  {len(CARRUSELES)} posts x ~6 slides")
    print(f"{'='*55}\n")

    total_slides = 0
    for folder, data in CARRUSELES.items():
        n = generate_post(folder, data)
        total_slides += n
        print(f"  ✓ {folder} ({n} slides)")

    # Guardar el calendario como JSON
    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump(SCHEDULE, f, indent=2, ensure_ascii=False)
    print(f"\n  schedule.json guardado con {len(SCHEDULE)} fechas")
    print(f"\nTotal: {len(CARRUSELES)} posts, {total_slides} slides generados.")

if __name__ == "__main__":
    main()
