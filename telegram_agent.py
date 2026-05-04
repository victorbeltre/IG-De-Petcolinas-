"""
telegram_agent.py — Agente de contenido PetColinas en Telegram.

Comandos:
  /start         - Bienvenida y guia de uso
  /post          - Genera el post del dia para Instagram
  /idea <tema>   - Genera post sobre un tema especifico

Chat natural: Claude responde como asesor de contenido de PetColinas.
Cuando genera un post muestra la imagen + caption con botones Publicar / Descartar.

Variables de entorno:
  TELEGRAM_BOT_TOKEN   - Token del bot (BotFather)
  ANTHROPIC_API_KEY    - API key de Claude
  IG_ACCESS_TOKEN      - Token de acceso de Instagram  (para publicar)
  INSTAGRAM_ACCOUNT_ID - ID de la cuenta de Instagram  (para publicar)
  GITHUB_PAT           - GitHub Personal Access Token  (para subir imagen)
"""

import asyncio
import base64
import datetime
import json
import logging
import os
import re
import sys
import time
import urllib.parse
from io import BytesIO

import anthropic
import requests
from PIL import Image
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

CLAUDE_MODEL = "claude-opus-4-7"
GITHUB_OWNER = "victorbeltre"
GITHUB_REPO = "ig-de-petcolinas-"
GITHUB_BRANCH = "main"
IMAGE_FILENAME = "post_del_dia.jpg"

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

SYSTEM_PROMPT = f"""Eres el asesor de marketing digital de PetColinas, una veterinaria y peluqueria canina en Santo Domingo, RD.

{PETCOLINAS}

Tu rol:
- Ayudas a crear contenido autentico para Instagram (@petcolinas)
- Cuando el usuario pide un post, idea o imagen, llamas a la herramienta generar_post
- Das consejos de marketing digital enfocados en mascotas y el mercado dominicano
- Respondes siempre en espanol con tono calido y dominicano
- Usas emojis con moderacion (maximo 3 por mensaje)

Si el usuario menciona querer publicar, post, contenido, idea para redes o similar -> llama generar_post.
"""

TOOLS = [
    {
        "name": "generar_post",
        "description": (
            "Genera un post completo para Instagram de PetColinas. "
            "Decide el tipo de contenido optimo para hoy, crea el prompt de imagen y el caption. "
            "Usar cuando el usuario pide un post, idea de contenido o imagen para Instagram."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tema": {
                    "type": "string",
                    "description": (
                        "Tema especifico solicitado por el usuario (ej: 'bano medicado', "
                        "'vacuna rabia', 'membresia plus'). Omitir para que Claude elija el mejor tema para hoy."
                    ),
                },
            },
            "required": [],
        },
    }
]


# ---------------------------------------------------------------------------
# Generacion de contenido (Claude + Pollinations FLUX-realism)
# ---------------------------------------------------------------------------

_claude_client: anthropic.Anthropic | None = None


def get_claude() -> anthropic.Anthropic:
    global _claude_client
    if _claude_client is None:
        _claude_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _claude_client


def generate_content_data(topic: str | None = None) -> dict:
    """Llama a Claude para generar tipo, tema, prompt de imagen y caption."""
    client = get_claude()
    today = datetime.date.today()
    weekday = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"][today.weekday()]
    breed = DOG_BREEDS[today.timetuple().tm_yday % len(DOG_BREEDS)]
    topic_line = f"Tema especifico solicitado: {topic}" if topic else "Elige el mejor tema para hoy segun el dia de la semana."

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system="Eres el estratega de contenido de PetColinas. Generas contenido autentico dominicano para Instagram.",
        messages=[{
            "role": "user",
            "content": f"""Hoy es {weekday} {today.strftime('%d de %B de %Y')}.
{PETCOLINAS}
Raza del dia para imagen: {breed}
{topic_line}
Tipos disponibles: {', '.join(CONTENT_TYPES)}

Responde SOLO con JSON valido (sin markdown ni texto extra):
{{
  "tipo": "<tipo>",
  "tema": "<tema especifico max 25 palabras>",
  "prompt_imagen": "<prompt INGLES para FLUX: {breed} recien baniado sentado mirando camara, salon grooming pared verde oscura, Sony A7III 85mm f2.0 natural light, 1 perro, 4 patas visibles, anatomia perfecta, no text. Max 80 palabras>",
  "caption": "<caption completo: gancho emoji + cuerpo calido dominicano + CTA + tel 809-752-6806 + Plaza Las Colinas + 10-12 hashtags. Max 2200 chars>"
}}"""
        }],
    )

    raw = response.content[0].text.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"Claude no retorno JSON valido:\n{raw}")
    return json.loads(match.group())


def generate_image_bytes(image_prompt: str) -> bytes:
    """Genera imagen 1080x1080 con FLUX-realism en Pollinations.ai y superpone logo."""
    seed = int(datetime.date.today().strftime("%Y%m%d"))
    photo_prefix = (
        "hyperrealistic DSLR photography, Sony A7III, 85mm portrait lens, f/2.0 aperture, "
        "natural window light, shallow depth of field, photojournalism quality, "
        "National Geographic style, fur texture detail, no AI artifacts, no plastic look. "
    )
    full_prompt = (photo_prefix + image_prompt)[:700]
    encoded = urllib.parse.quote(full_prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1080&height=1080&model=flux-realism&nologo=true&seed={seed}&enhance=true"
    )

    logger.info("Generando imagen con FLUX-REALISM...")
    resp = requests.get(url, timeout=180)
    resp.raise_for_status()

    img = Image.open(BytesIO(resp.content)).convert("RGB")
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
        except Exception as e:
            logger.warning(f"No se pudo agregar logo: {e}")

    output = BytesIO()
    img.save(output, format="JPEG", quality=95)
    return output.getvalue()


# ---------------------------------------------------------------------------
# GitHub upload
# ---------------------------------------------------------------------------

def upload_image_to_github(image_bytes: bytes) -> str:
    """Sube imagen al repo y retorna la URL raw publica."""
    pat = os.getenv("GITHUB_PAT")
    if not pat:
        raise EnvironmentError("Falta GITHUB_PAT para subir imagen a GitHub")

    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{IMAGE_FILENAME}"

    existing = requests.get(api_url, headers=headers).json()
    sha = existing.get("sha")

    payload = {
        "message": f"Post manual PetColinas {datetime.date.today()}",
        "content": base64.b64encode(image_bytes).decode(),
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    resp = requests.put(api_url, headers=headers, json=payload)
    if resp.status_code not in (200, 201):
        raise Exception(f"Error subiendo imagen a GitHub: {resp.status_code} — {resp.text[:200]}")

    return f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{IMAGE_FILENAME}"


# ---------------------------------------------------------------------------
# Instagram publish
# ---------------------------------------------------------------------------

def _wait_until_ready(acc_id: str, creation_id: str, token: str, timeout: int = 90) -> bool:
    waited = 0
    while waited < timeout:
        r = requests.get(
            f"https://graph.facebook.com/v19.0/{creation_id}",
            params={"fields": "status_code", "access_token": token},
        ).json()
        status = r.get("status_code", "UNKNOWN")
        logger.info(f"IG container status: {status}")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            logger.error(f"Error en container IG: {r}")
            return False
        time.sleep(5)
        waited += 5
    return False


def publish_to_instagram(image_url: str, caption: str) -> str:
    """Publica en Instagram. Retorna el post_id."""
    token = os.environ["IG_ACCESS_TOKEN"]
    acc_id = os.environ["INSTAGRAM_ACCOUNT_ID"]

    r = requests.post(
        f"https://graph.facebook.com/v19.0/{acc_id}/media",
        data={"image_url": image_url, "caption": caption, "access_token": token},
    ).json()

    if "error" in r:
        raise Exception(f"Error Meta API (container): {r['error'].get('message', r)}")

    creation_id = r["id"]
    logger.info(f"Container IG creado: {creation_id}")

    if not _wait_until_ready(acc_id, creation_id, token):
        raise Exception("Instagram no proceso la imagen a tiempo (timeout 90s)")

    pub = requests.post(
        f"https://graph.facebook.com/v19.0/{acc_id}/media_publish",
        data={"creation_id": creation_id, "access_token": token},
    ).json()

    if "error" in pub:
        raise Exception(f"Error Meta API (publicar): {pub['error'].get('message', pub)}")

    return pub.get("id", "?")


# ---------------------------------------------------------------------------
# Helpers de UI
# ---------------------------------------------------------------------------

def _can_publish() -> bool:
    return bool(
        os.getenv("IG_ACCESS_TOKEN")
        and os.getenv("INSTAGRAM_ACCOUNT_ID")
        and os.getenv("GITHUB_PAT")
    )


def _post_keyboard() -> InlineKeyboardMarkup:
    if _can_publish():
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Publicar en Instagram", callback_data="publish"),
            InlineKeyboardButton("❌ Descartar", callback_data="discard"),
        ]])
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ Descartar", callback_data="discard"),
    ]])


async def _send_post_preview(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    content: dict,
    image_bytes: bytes,
):
    """Guarda post en user_data y envia preview con botones."""
    context.user_data["pending_post"] = {
        "image_bytes": image_bytes,
        "caption": content["caption"],
        "tipo": content["tipo"],
        "tema": content["tema"],
        "shown": False,
    }

    caption_preview = content["caption"]
    if len(caption_preview) > 900:
        caption_preview = caption_preview[:897] + "..."

    await update.effective_message.reply_photo(
        photo=BytesIO(image_bytes),
        caption=f"*{content['tipo'].upper()} — {content['tema']}*\n\n{caption_preview}",
        parse_mode="Markdown",
        reply_markup=_post_keyboard(),
    )

    if not _can_publish():
        await update.effective_message.reply_text(
            "⚠️ Para publicar directamente configura: `IG_ACCESS_TOKEN`, `INSTAGRAM_ACCOUNT_ID`, `GITHUB_PAT`",
            parse_mode="Markdown",
        )

    context.user_data["pending_post"]["shown"] = True


# ---------------------------------------------------------------------------
# Flujo completo de generacion (usado por /post, /idea y chat natural)
# ---------------------------------------------------------------------------

async def _generate_and_send(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    topic: str | None = None,
):
    progress = await update.effective_message.reply_text("⏳ Generando contenido con Claude...")
    try:
        content = generate_content_data(topic)
        await progress.edit_text(
            f"🎨 Generando imagen con FLUX-Realism...\n_Tipo: {content['tipo']} · {content['tema']}_",
            parse_mode="Markdown",
        )
        image_bytes = generate_image_bytes(content["prompt_imagen"])
        await progress.delete()
        await _send_post_preview(update, context, content, image_bytes)
    except Exception as e:
        await progress.edit_text(f"❌ Error generando el post: {e}")
        logger.exception("Error en _generate_and_send")


# ---------------------------------------------------------------------------
# Comando /start
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = "✅ Publicacion en Instagram lista" if _can_publish() else "⚠️ Publicacion no configurada (faltan secrets)"
    await update.message.reply_text(
        "🐾 *Agente de Contenido PetColinas*\n\n"
        "Soy tu asistente para crear posts de Instagram para @petcolinas. "
        "Puedo generar la imagen y el caption, y publicar directamente.\n\n"
        "*Comandos:*\n"
        "• /post — Genera el post del dia\n"
        "• /idea grooming — Post sobre grooming\n"
        "• /idea vacunas — Post sobre vacunas\n\n"
        "*O escribeme directamente:*\n"
        "_\"Dame una idea para hoy\"_\n"
        "_\"Genera algo sobre la membresía Plus\"_\n"
        "_\"¿Cuánto cuesta el baño medicado?\"_\n\n"
        f"{status}",
        parse_mode="Markdown",
    )


# ---------------------------------------------------------------------------
# Comando /post
# ---------------------------------------------------------------------------

async def cmd_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _generate_and_send(update, context, topic=None)


# ---------------------------------------------------------------------------
# Comando /idea <tema>
# ---------------------------------------------------------------------------

async def cmd_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        topic = " ".join(context.args)
        await _generate_and_send(update, context, topic=topic)
    else:
        await update.message.reply_text(
            "Indica el tema. Ejemplos:\n"
            "`/idea bano medicado`\n"
            "`/idea membresia plus`\n"
            "`/idea vacuna rabia`",
            parse_mode="Markdown",
        )


# ---------------------------------------------------------------------------
# Callback de botones (Publicar / Descartar)
# ---------------------------------------------------------------------------

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "discard":
        context.user_data.pop("pending_post", None)
        await query.edit_message_caption(caption="🗑️ Post descartado.")
        return

    if query.data != "publish":
        return

    pending = context.user_data.get("pending_post")
    if not pending or "image_bytes" not in pending:
        await query.edit_message_caption(caption="❌ No hay post pendiente.")
        return

    try:
        await query.edit_message_caption(
            caption=f"*{pending['tipo'].upper()} — {pending['tema']}*\n\n⏳ Subiendo imagen a GitHub...",
            parse_mode="Markdown",
        )

        image_url = await asyncio.get_event_loop().run_in_executor(
            None, upload_image_to_github, pending["image_bytes"]
        )

        await query.edit_message_caption(
            caption=f"*{pending['tipo'].upper()} — {pending['tema']}*\n\n✅ Imagen subida. Esperando CDN (15s)...",
            parse_mode="Markdown",
        )
        await asyncio.sleep(15)

        await query.edit_message_caption(
            caption=f"*{pending['tipo'].upper()} — {pending['tema']}*\n\n📲 Publicando en Instagram...",
            parse_mode="Markdown",
        )

        post_id = await asyncio.get_event_loop().run_in_executor(
            None, publish_to_instagram, image_url, pending["caption"]
        )

        context.user_data.pop("pending_post", None)
        await query.edit_message_caption(
            caption=f"🎉 *Publicado en @petcolinas!*\nID: `{post_id}`",
            parse_mode="Markdown",
        )

    except Exception as e:
        logger.exception("Error publicando en Instagram desde Telegram")
        await query.edit_message_caption(caption=f"❌ Error al publicar: {e}")


# ---------------------------------------------------------------------------
# Chat natural con Claude (agentic loop)
# ---------------------------------------------------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if "history" not in context.user_data:
        context.user_data["history"] = []

    context.user_data["history"].append({"role": "user", "content": user_text})
    # Mantener solo los ultimos 10 turnos para no sobrecargar el contexto
    if len(context.user_data["history"]) > 10:
        context.user_data["history"] = context.user_data["history"][-10:]

    thinking_msg = await update.message.reply_text("💭 Pensando...")
    client = get_claude()

    # Agentic loop: Claude puede llamar herramientas hasta llegar a una respuesta final
    messages = list(context.user_data["history"])
    generated_content: dict | None = None
    generated_image: bytes | None = None

    try:
        while True:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1500,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            if response.stop_reason != "tool_use":
                break

            tool_uses = [b for b in response.content if b.type == "tool_use"]
            tool_results = []

            for tool_use in tool_uses:
                if tool_use.name != "generar_post":
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": json.dumps({"error": f"herramienta desconocida: {tool_use.name}"}),
                    })
                    continue

                topic = tool_use.input.get("tema") or None
                label = f"sobre «{topic}»" if topic else "del dia"
                await thinking_msg.edit_text(f"⏳ Generando post {label}...")

                try:
                    content = await asyncio.get_event_loop().run_in_executor(
                        None, generate_content_data, topic
                    )
                    await thinking_msg.edit_text(
                        f"🎨 Generando imagen: {content['tema']}..."
                    )
                    image_bytes = await asyncio.get_event_loop().run_in_executor(
                        None, generate_image_bytes, content["prompt_imagen"]
                    )
                    generated_content = content
                    generated_image = image_bytes
                    result = json.dumps({
                        "success": True,
                        "tipo": content["tipo"],
                        "tema": content["tema"],
                        "message": "Post generado correctamente. Dile al usuario que puede publicarlo.",
                    }, ensure_ascii=False)
                except Exception as e:
                    result = json.dumps({"error": str(e)})

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result,
                })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        # Extraer texto final
        assistant_text = next(
            (b.text for b in response.content if hasattr(b, "text") and b.text),
            "Aqui tienes el post generado.",
        )

        # Guardar en historial (solo texto, no tool_use blocks)
        context.user_data["history"].append({"role": "assistant", "content": assistant_text})

        await thinking_msg.delete()

        # Si se genero un post, enviarlo con botones
        if generated_content and generated_image:
            await update.message.reply_text(assistant_text)
            await _send_post_preview(update, context, generated_content, generated_image)
        else:
            await update.message.reply_text(assistant_text)

    except Exception as e:
        await thinking_msg.edit_text(f"❌ Error: {e}")
        logger.exception("Error en handle_message")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: falta la variable de entorno TELEGRAM_BOT_TOKEN")
        sys.exit(1)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: falta la variable de entorno ANTHROPIC_API_KEY")
        sys.exit(1)

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("post", cmd_post))
    app.add_handler(CommandHandler("idea", cmd_idea))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Agente PetColinas iniciado. Esperando mensajes en Telegram...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
