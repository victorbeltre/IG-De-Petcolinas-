#!/usr/bin/env python3
"""
bridge_video.py — Lado servidor del puente de VIDEO (corre en GitHub Actions).

Lee video_requests/pending.json y genera un video con Gemini Omni Flash
(gemini-omni-1.1-flash) usando el secret GOOGLE_AI_KEY. El resultado se guarda en
video_requests/output/<id>/ junto con meta.json.

Tope de gasto: cuenta cada intento antes de llamar a la API en
video_requests/usage.json. Si el mes ya llego al limite, no llama a la API.
La API key se lee del entorno y NUNCA se imprime.
"""

import base64
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PENDING = Path("video_requests/pending.json")
OUTPUT_ROOT = Path("video_requests/output")
USAGE = Path("video_requests/usage.json")

MODELO = "gemini-omni-1.1-flash"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"

# Tope mensual de videos. El precio de Omni Flash no esta publicado en la
# pagina de precios, asi que el tope va por cantidad hasta confirmar el costo.
MAX_VIDEOS_POR_MES = int(os.environ.get("MAX_VIDEOS_POR_MES", "3"))

ASPECTOS = {"9:16", "16:9"}
RESOLUCIONES = {"360p", "720p", "1080p"}


def mes_actual() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def leer_uso() -> dict:
    if USAGE.exists():
        return json.loads(USAGE.read_text(encoding="utf-8"))
    return {}


def guardar_uso(uso: dict) -> None:
    USAGE.parent.mkdir(parents=True, exist_ok=True)
    USAGE.write_text(json.dumps(uso, indent=2), encoding="utf-8")


def buscar_video(obj):
    """Busca bytes de video (base64) o una URI dentro de la respuesta, sin importar la forma exacta."""
    if isinstance(obj, dict):
        mime = str(obj.get("mime_type") or obj.get("mimeType") or "")
        if mime.startswith("video/") and obj.get("data"):
            return ("b64", obj["data"])
        if isinstance(obj.get("output_video"), dict) and obj["output_video"].get("data"):
            return ("b64", obj["output_video"]["data"])
        if mime.startswith("video/") and obj.get("uri"):
            return ("uri", obj["uri"])
        for v in obj.values():
            hallado = buscar_video(v)
            if hallado:
                return hallado
    elif isinstance(obj, list):
        for v in obj:
            hallado = buscar_video(v)
            if hallado:
                return hallado
    return None


def main() -> None:
    if not PENDING.exists():
        print("No hay pending.json; nada que generar.")
        return

    try:
        req = json.loads(PENDING.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: pending.json invalido: {e}")

    req_id = str(req.get("id", "")).strip()
    prompt = str(req.get("prompt", "")).strip()
    if not req_id or not prompt:
        sys.exit("ERROR: el pedido necesita 'id' y 'prompt'.")

    aspect = req.get("aspect", "9:16")
    if aspect not in ASPECTOS:
        aspect = "9:16"
    resolucion = req.get("resolution", "720p")
    if resolucion not in RESOLUCIONES:
        resolucion = "720p"

    out_dir = OUTPUT_ROOT / req_id
    if out_dir.exists() and any(out_dir.glob("*.mp4")):
        print(f"El pedido {req_id} ya tiene video; se omite.")
        return

    # Tope mensual, contado antes de llamar a la API.
    uso = leer_uso()
    clave = mes_actual()
    usados = int(uso.get(clave, 0))
    if usados >= MAX_VIDEOS_POR_MES:
        out_dir.mkdir(parents=True, exist_ok=True)
        meta = {"id": req_id, "status": "cap_reached", "usados_mes": usados,
                "limite_mes": MAX_VIDEOS_POR_MES, "prompt": prompt}
        (out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Tope mensual alcanzado ({usados}/{MAX_VIDEOS_POR_MES}); no se llamo a la API.")
        return

    uso[clave] = usados + 1
    guardar_uso(uso)

    key = os.environ.get("GOOGLE_AI_KEY", "").strip()
    if not key:
        sys.exit("ERROR: falta GOOGLE_AI_KEY en el entorno.")

    import requests

    headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
    payload = {
        "model": MODELO,
        "input": prompt,
        "response_format": {"type": "video", "aspect_ratio": aspect, "resolution": resolucion},
    }

    print(f"Generando video {req_id}: aspect={aspect} resolution={resolucion} (mes {clave}: {usados + 1}/{MAX_VIDEOS_POR_MES})")
    try:
        resp = requests.post(ENDPOINT, headers=headers, json=payload, timeout=600)
    except requests.RequestException as e:
        sys.exit(f"ERROR de red: {type(e).__name__}")
    if resp.status_code != 200:
        # Sin headers ni URL en el mensaje, para no filtrar la key.
        sys.exit(f"ERROR (HTTP {resp.status_code}): {resp.text[:400]}")

    data = resp.json()
    hallado = buscar_video(data)
    if not hallado:
        print("Claves de la respuesta:", list(data.keys()))
        sys.exit("ERROR: la respuesta no trae video (posible filtro de seguridad o formato nuevo).")

    tipo, valor = hallado
    if tipo == "b64":
        video_bytes = base64.b64decode(valor)
    else:
        r = requests.get(valor, headers={"x-goog-api-key": key}, timeout=600)
        if r.status_code != 200:
            sys.exit(f"ERROR al bajar el video (HTTP {r.status_code}).")
        video_bytes = r.content

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "video.mp4").write_bytes(video_bytes)
    meta = {
        "id": req_id,
        "prompt": prompt,
        "model": MODELO,
        "aspect": aspect,
        "resolution": resolucion,
        "files": ["video.mp4"],
        "status": "done",
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: video en {out_dir / 'video.mp4'}")


if __name__ == "__main__":
    main()
