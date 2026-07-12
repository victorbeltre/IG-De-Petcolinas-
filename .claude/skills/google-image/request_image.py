#!/usr/bin/env python3
"""
request_image.py — Cliente del PUENTE de imagenes (GitHub como puente).

Genera imagenes con Google Imagen 4 SIN tener la API key en la maquina.
El flujo real de generacion corre en GitHub Actions, que si tiene la key
en los Secrets del repo.

Como funciona:
  1. Escribe un pedido en image_requests/pending.json y lo hace push.
  2. El push dispara el workflow 'generar_imagen.yml' en GitHub.
  3. El workflow genera la imagen con Imagen 4 y la commitea de vuelta.
  4. Este script espera (git fetch en bucle) y baja la imagen resultante.

Uso:
  python request_image.py "un golden retriever feliz en un parque" --out perro.png
  python request_image.py "afiche ..." --n 2 --aspect 1:1 --model standard

Requisitos:
  - git configurado con acceso (push) al repo del puente. NO se necesita
    ninguna API key local: la key vive en los Secrets de GitHub.
  - python 3.9+ (solo libreria estandar).

Config: bridge.json (junto a este archivo) define repo_url y branch.
"""

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "bridge.json").read_text(encoding="utf-8"))
REPO_URL = os.environ.get("IMAGEN_BRIDGE_REPO", CONFIG["repo_url"])
BRANCH = os.environ.get("IMAGEN_BRIDGE_BRANCH", CONFIG["branch"])
# Checkout dedicado del puente (solo archivos del repo, ningun secreto).
WORKDIR = Path(os.environ.get(
    "IMAGEN_BRIDGE_DIR",
    Path.home() / ".cache" / "imagen-bridge" / "repo",
))

POLL_SECONDS = 8
TIMEOUT_SECONDS = 240  # 4 min


def git(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), check=check,
        capture_output=True, text=True,
    )


def preparar_repo() -> None:
    """Clona (una vez) o actualiza el checkout del puente en WORKDIR."""
    if (WORKDIR / ".git").exists():
        git("fetch", "origin", BRANCH, cwd=WORKDIR)
        git("checkout", "-B", BRANCH, f"origin/{BRANCH}", cwd=WORKDIR)
        git("reset", "--hard", f"origin/{BRANCH}", cwd=WORKDIR)
        return
    WORKDIR.parent.mkdir(parents=True, exist_ok=True)
    if WORKDIR.exists():
        shutil.rmtree(WORKDIR)
    print("Clonando el repo del puente (una sola vez)...", file=sys.stderr)
    r = git("clone", "--depth", "20", "--branch", BRANCH, REPO_URL, str(WORKDIR),
            cwd=WORKDIR.parent, check=False)
    if r.returncode != 0:
        sys.exit(f"ERROR al clonar el repo del puente:\n{r.stderr.strip()}")


def nuevo_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    suf = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(4))
    return f"{ts}-{suf}"


def enviar_pedido(req: dict) -> None:
    reqdir = WORKDIR / "image_requests"
    reqdir.mkdir(parents=True, exist_ok=True)
    (reqdir / "pending.json").write_text(
        json.dumps(req, ensure_ascii=False, indent=2), encoding="utf-8")
    git("add", "image_requests/pending.json", cwd=WORKDIR)
    git("-c", "user.name=Imagen Bridge",
        "-c", "user.email=petcolinasrd@gmail.com",
        "commit", "-m", f"Pedido de imagen {req['id']}", cwd=WORKDIR)
    r = git("push", "origin", BRANCH, cwd=WORKDIR, check=False)
    if r.returncode != 0:
        sys.exit(f"ERROR al hacer push del pedido:\n{r.stderr.strip()}")


def esperar_resultado(req_id: str) -> Path:
    out_rel = Path("image_requests/output") / req_id
    print(f"Esperando a que GitHub genere la imagen (hasta {TIMEOUT_SECONDS//60} min)...",
          file=sys.stderr)
    inicio = time.monotonic()
    while time.monotonic() - inicio < TIMEOUT_SECONDS:
        time.sleep(POLL_SECONDS)
        git("fetch", "origin", BRANCH, cwd=WORKDIR, check=False)
        git("reset", "--hard", f"origin/{BRANCH}", cwd=WORKDIR, check=False)
        meta = WORKDIR / out_rel / "meta.json"
        if meta.exists():
            return WORKDIR / out_rel
    sys.exit("ERROR: se agoto el tiempo esperando la imagen. "
             "Revisa la pestana Actions del repo por si el workflow fallo.")


def main() -> None:
    p = argparse.ArgumentParser(description="Genera imagenes via el puente de GitHub (Imagen 4).")
    p.add_argument("prompt", nargs="?", help="Descripcion (imagen normal) o fondo (afiche).")
    p.add_argument("--out", default="image.png")
    p.add_argument("--n", type=int, default=1)
    p.add_argument("--aspect", default="1:1", choices=["1:1", "3:4", "4:3", "9:16", "16:9"])
    p.add_argument("--model", default="standard", choices=["fast", "standard", "ultra"])
    p.add_argument("--no-people", action="store_true")
    # --- Modo AFICHE de marca PetColinas ---
    p.add_argument("--afiche", action="store_true", help="Renderiza un afiche de marca PetColinas.")
    p.add_argument("--titulo", help="Titular del afiche.")
    p.add_argument("--subtitulo", help="Subtitulo dorado del afiche.")
    p.add_argument("--punto", action="append", default=[], help="Vineta del afiche (repetible).")
    p.add_argument("--cta", help="Texto de la barra naranja (ej 'WhatsApp: 809-...').")
    p.add_argument("--bg", help="Descripcion del fondo del afiche.")
    args = p.parse_args()

    es_afiche = args.afiche or bool(args.titulo)
    if es_afiche:
        if not args.titulo:
            sys.exit("ERROR: para un afiche usa --titulo (y opcional --subtitulo/--punto/--cta/--bg).")
        req = {
            "id": nuevo_id(),
            "type": "afiche",
            "titulo": args.titulo,
            "subtitulo": args.subtitulo or "",
            "puntos": args.punto,
            "cta": args.cta or "",
            "bg_prompt": args.bg or args.prompt or "",
        }
    else:
        if not args.prompt:
            sys.exit("ERROR: falta el prompt. Ej: request_image.py \"un perro feliz\" --out perro.png")
        req = {
            "id": nuevo_id(),
            "type": "imagen",
            "prompt": args.prompt,
            "n": max(1, min(4, args.n)),
            "aspect": args.aspect,
            "model": args.model,
            "no_people": bool(args.no_people),
        }

    preparar_repo()
    enviar_pedido(req)
    carpeta = esperar_resultado(req["id"])

    # Copiamos las imagenes al destino pedido.
    pngs = sorted(carpeta.glob("*.png"))
    if not pngs:
        sys.exit("ERROR: el workflow no dejo imagenes en la carpeta de salida.")

    out = Path(args.out)
    destinos = []
    if len(pngs) == 1:
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(pngs[0], out)
        destinos.append(out)
    else:
        base, ext = out.with_suffix(""), (out.suffix or ".png")
        for i, src in enumerate(pngs, 1):
            d = Path(f"{base}_{i}{ext}")
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, d)
            destinos.append(d)

    print(f"OK: {len(destinos)} imagen(es) generada(s) via GitHub:")
    for d in destinos:
        print(f"  {d}")


if __name__ == "__main__":
    main()
