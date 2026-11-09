#!/usr/bin/env python3
"""
request_video.py — Cliente del PUENTE de video (Gemini Omni Flash, via GitHub).

Uso:
  python request_video.py "prompt del video" --out clip.mp4
  python request_video.py "prompt" --aspect 16:9 --resolution 1080p --out clip.mp4

Escribe video_requests/pending.json, lo sube al repo del puente y espera
a que GitHub Actions deje video_requests/output/<id>/meta.json. No necesita
ninguna API key local: la key vive en los Secrets del repo.
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

REPO_URL = os.environ.get("VIDEO_BRIDGE_REPO", "https://github.com/victorbeltre/IG-De-Petcolinas-.git")
BRANCH = os.environ.get("VIDEO_BRIDGE_BRANCH", "main")
WORKDIR = Path(os.environ.get("VIDEO_BRIDGE_DIR", Path.home() / ".cache" / "imagen-bridge" / "repo"))

POLL_SECONDS = 10
TIMEOUT_SECONDS = 900  # 15 min


def git(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), check=check, capture_output=True, text=True)


def preparar_repo() -> None:
    if (WORKDIR / ".git").exists():
        git("fetch", "origin", BRANCH, cwd=WORKDIR)
        git("checkout", "-B", BRANCH, f"origin/{BRANCH}", cwd=WORKDIR)
        git("reset", "--hard", f"origin/{BRANCH}", cwd=WORKDIR)
        return
    WORKDIR.parent.mkdir(parents=True, exist_ok=True)
    if WORKDIR.exists():
        shutil.rmtree(WORKDIR)
    r = git("clone", "--depth", "20", "--branch", BRANCH, REPO_URL, str(WORKDIR), cwd=WORKDIR.parent, check=False)
    if r.returncode != 0:
        sys.exit(f"ERROR al clonar el repo del puente:\n{r.stderr.strip()}")


def nuevo_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    suf = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(4))
    return f"{ts}-{suf}"


def enviar_pedido(req: dict) -> None:
    carpeta = WORKDIR / "video_requests"
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "pending.json").write_text(json.dumps(req, ensure_ascii=False, indent=2), encoding="utf-8")
    git("add", "video_requests/pending.json", cwd=WORKDIR)
    git("-c", "user.name=Video Bridge", "-c", "user.email=petcolinasrd@gmail.com",
        "commit", "-m", f"Pedido de video {req['id']}", cwd=WORKDIR)
    r = git("push", "origin", BRANCH, cwd=WORKDIR, check=False)
    if r.returncode != 0:
        sys.exit(f"ERROR al hacer push del pedido:\n{r.stderr.strip()}")


def esperar_resultado(req_id: str) -> Path:
    rel = Path("video_requests/output") / req_id
    inicio = time.monotonic()
    while time.monotonic() - inicio < TIMEOUT_SECONDS:
        time.sleep(POLL_SECONDS)
        git("fetch", "origin", BRANCH, cwd=WORKDIR, check=False)
        git("reset", "--hard", f"origin/{BRANCH}", cwd=WORKDIR, check=False)
        meta = WORKDIR / rel / "meta.json"
        if meta.exists():
            return WORKDIR / rel
    sys.exit("ERROR: se agoto el tiempo esperando el video. Revisa la pestana Actions del repo.")


def main() -> None:
    p = argparse.ArgumentParser(description="Genera un video corto via el puente de GitHub (Omni Flash).")
    p.add_argument("prompt")
    p.add_argument("--out", default="video.mp4")
    p.add_argument("--aspect", default="9:16", choices=["9:16", "16:9"])
    p.add_argument("--resolution", default="720p", choices=["360p", "720p", "1080p"])
    args = p.parse_args()

    preparar_repo()
    req = {"id": nuevo_id(), "prompt": args.prompt, "aspect": args.aspect, "resolution": args.resolution}
    enviar_pedido(req)
    print("Pedido enviado; esperando el video...", file=sys.stderr)
    resultado = esperar_resultado(req["id"])
    meta = json.loads((resultado / "meta.json").read_text(encoding="utf-8"))

    if meta.get("status") == "cap_reached":
        sys.exit(f"Tope mensual alcanzado ({meta.get('usados_mes')}/{meta.get('limite_mes')}). No se genero el video.")
    if meta.get("status") != "done":
        sys.exit(f"ERROR: el puente devolvio estado {meta.get('status')}.")

    destino = Path(args.out).resolve()
    shutil.copy(resultado / "video.mp4", destino)
    print(f"OK: {destino}")


if __name__ == "__main__":
    main()
