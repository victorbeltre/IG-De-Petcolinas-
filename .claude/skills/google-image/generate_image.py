#!/usr/bin/env python3
"""
generate_image.py — Genera imagenes con Google Imagen 4 desde un prompt de texto.

Uso basico:
  python generate_image.py "un golden retriever feliz en un parque, luz natural"

Opciones:
  --out RUTA      Archivo de salida (por defecto: image.png en el cwd)
  --n N           Cantidad de imagenes 1-4 (por defecto 1)
  --aspect A      Relacion de aspecto: 1:1, 3:4, 4:3, 9:16, 16:9 (por defecto 1:1)
  --model M       fast | standard | ultra (por defecto standard)
  --no-people     No generar personas (por defecto se permiten adultos)

Requisitos:
  - Variable de entorno GOOGLE_AI_KEY con tu API key de Google AI Studio
    (o un archivo ~/.google_ai_key con la key dentro).
  - pip install requests

Seguridad:
  La API key se lee del entorno o de un archivo local y NUNCA se imprime
  en pantalla ni en los mensajes de error. La key viaja en un header, no
  en la URL, para que ningun log la filtre.
"""

import argparse
import base64
import os
import sys
import time
from pathlib import Path

MODELOS = {
    "fast": "imagen-4.0-fast-generate-001",
    "standard": "imagen-4.0-generate-001",
    "ultra": "imagen-4.0-ultra-generate-001",
}


def obtener_key() -> str:
    """Lee la API key del entorno o de un archivo local. Nunca la imprime."""
    key = os.environ.get("GOOGLE_AI_KEY", "").strip()
    if not key:
        for ruta in (
            Path.home() / ".google_ai_key",
            Path.home() / ".config" / "google_ai" / "key",
        ):
            try:
                if ruta.exists():
                    key = ruta.read_text(encoding="utf-8").strip()
                    if key:
                        break
            except OSError:
                pass
    if not key:
        sys.exit(
            "ERROR: No hay API key.\n"
            "  Define la variable de entorno GOOGLE_AI_KEY, por ejemplo:\n"
            "    export GOOGLE_AI_KEY='AIza...'\n"
            "  o guarda la key en el archivo ~/.google_ai_key"
        )
    return key


def generar(prompt: str, out: Path, n: int, aspect: str, model: str, person: str) -> list[Path]:
    # Validamos la key primero: asi el aviso sale limpio aunque falte 'requests'.
    key = obtener_key()

    try:
        import requests
    except ModuleNotFoundError:
        sys.exit("ERROR: falta la libreria 'requests'. Instalala con:  pip install requests")

    model_id = MODELOS.get(model, MODELOS["standard"])
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:predict"
    headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": n,
            "aspectRatio": aspect,
            "personGeneration": person,
        },
    }

    ultimo_error = ""
    for intento in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                preds = data.get("predictions", [])
                if not preds:
                    sys.exit("ERROR: La API no devolvio imagenes (posible filtro de seguridad).")
                salidas = []
                base = out.with_suffix("")
                ext = out.suffix or ".png"
                for i, pred in enumerate(preds):
                    b64 = pred.get("bytesBase64Encoded")
                    if not b64:
                        continue
                    destino = out if len(preds) == 1 else Path(f"{base}_{i + 1}{ext}")
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    destino.write_bytes(base64.b64decode(b64))
                    salidas.append(destino)
                return salidas
            # No imprimimos headers ni URL para no filtrar la key.
            ultimo_error = f"HTTP {resp.status_code}"
            if resp.status_code in (400, 403):
                # Errores no recuperables: mostramos el detalle (sin la key).
                detalle = resp.text[:500]
                sys.exit(f"ERROR ({ultimo_error}): {detalle}")
        except requests.RequestException as e:
            ultimo_error = type(e).__name__
        if intento < 2:
            time.sleep(6)
    sys.exit(f"ERROR: No se pudo generar la imagen tras 3 intentos ({ultimo_error}).")


def main() -> None:
    p = argparse.ArgumentParser(description="Genera imagenes con Google Imagen 4.")
    p.add_argument("prompt", help="Descripcion de la imagen a generar.")
    p.add_argument("--out", default="image.png", help="Archivo de salida (default: image.png)")
    p.add_argument("--n", type=int, default=1, help="Cantidad de imagenes 1-4 (default 1)")
    p.add_argument("--aspect", default="1:1",
                   choices=["1:1", "3:4", "4:3", "9:16", "16:9"],
                   help="Relacion de aspecto (default 1:1)")
    p.add_argument("--model", default="standard",
                   choices=["fast", "standard", "ultra"],
                   help="Modelo Imagen 4 (default standard)")
    p.add_argument("--no-people", action="store_true",
                   help="No generar personas.")
    args = p.parse_args()

    n = max(1, min(4, args.n))
    person = "dont_allow" if args.no_people else "allow_adult"

    salidas = generar(args.prompt, Path(args.out), n, args.aspect, args.model, person)
    print(f"OK: {len(salidas)} imagen(es) generada(s):")
    for s in salidas:
        print(f"  {s}")


if __name__ == "__main__":
    main()
