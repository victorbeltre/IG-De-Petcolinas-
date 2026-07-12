#!/usr/bin/env python3
"""
bridge_generate.py — Lado servidor del puente de imagenes (corre en GitHub Actions).

Lee image_requests/pending.json y genera la(s) imagen(es) con Imagen 4 usando
el secret GOOGLE_AI_KEY (inyectado como variable de entorno por el workflow).
Guarda el resultado en image_requests/output/<id>/ junto con un meta.json.

La API key se lee del entorno y NUNCA se imprime.
"""

import base64
import json
import os
import sys
import time
from pathlib import Path

PENDING = Path("image_requests/pending.json")
OUTPUT_ROOT = Path("image_requests/output")

MODELOS = {
    "fast": "imagen-4.0-fast-generate-001",
    "standard": "imagen-4.0-generate-001",
    "ultra": "imagen-4.0-ultra-generate-001",
}
ASPECTOS = {"1:1", "3:4", "4:3", "9:16", "16:9"}


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

    n = max(1, min(4, int(req.get("n", 1))))
    aspect = req.get("aspect", "1:1")
    if aspect not in ASPECTOS:
        aspect = "1:1"
    model = req.get("model", "standard")
    model_id = MODELOS.get(model, MODELOS["standard"])
    person = "dont_allow" if req.get("no_people") else "allow_adult"

    out_dir = OUTPUT_ROOT / req_id
    # Si ya existe una imagen para este id, no regeneramos (idempotente).
    if out_dir.exists() and any(out_dir.glob("*.png")):
        print(f"El pedido {req_id} ya tiene imagenes; se omite.")
        return

    key = os.environ.get("GOOGLE_AI_KEY", "").strip()
    if not key:
        sys.exit("ERROR: falta GOOGLE_AI_KEY en el entorno.")

    import requests

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:predict"
    headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": n, "aspectRatio": aspect, "personGeneration": person},
    }

    print(f"Generando pedido {req_id}: n={n} aspect={aspect} model={model}")

    data = None
    ultimo = ""
    for intento in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                break
            ultimo = f"HTTP {resp.status_code}"
            # No imprimimos headers/URL para no filtrar la key.
            if resp.status_code in (400, 403):
                sys.exit(f"ERROR ({ultimo}): {resp.text[:400]}")
        except requests.RequestException as e:
            ultimo = type(e).__name__
        if intento < 2:
            time.sleep(6)

    if data is None:
        sys.exit(f"ERROR: no se pudo generar tras 3 intentos ({ultimo}).")

    preds = data.get("predictions", [])
    if not preds:
        sys.exit("ERROR: la API no devolvio imagenes (posible filtro de seguridad).")

    out_dir.mkdir(parents=True, exist_ok=True)
    guardadas = []
    for i, pred in enumerate(preds, 1):
        b64 = pred.get("bytesBase64Encoded")
        if not b64:
            continue
        nombre = "image.png" if len(preds) == 1 else f"image_{i}.png"
        (out_dir / nombre).write_bytes(base64.b64decode(b64))
        guardadas.append(nombre)

    meta = {
        "id": req_id,
        "prompt": prompt,
        "n": n,
        "aspect": aspect,
        "model": model,
        "no_people": bool(req.get("no_people")),
        "files": guardadas,
        "status": "done",
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {len(guardadas)} imagen(es) en {out_dir}")


if __name__ == "__main__":
    main()
