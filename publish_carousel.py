"""
Publica un carrusel de imagenes en Instagram via Meta Graph API.

Variables de entorno requeridas:
  IG_ACCESS_TOKEN      -> Token de acceso de Meta
  INSTAGRAM_ACCOUNT_ID -> ID numerico de la cuenta de Instagram
  POST_DIR             -> Nombre de la carpeta en posts/ (ej: "semana-01")

Variables opcionales (se inyectan automaticamente desde el workflow):
  REPO   -> owner/repo de GitHub para construir URLs raw publicas
  BRANCH -> rama del repo

Flujo:
  1. Lee imagenes ordenadas de posts/<POST_DIR>/ (01.png, 02.png, ..., maximo 10)
  2. Lee caption de posts/<POST_DIR>/caption.txt
  3. Crea item containers con is_carousel_item=true
  4. Crea contenedor CAROUSEL padre
  5. Espera status FINISHED
  6. Publica con media_publish
"""

import os
import sys
import time
import glob
import requests

GRAPH_API = "https://graph.facebook.com/v19.0"
VALID_EXTENSIONS = (".png", ".jpg", ".jpeg")


def get_image_files(post_dir: str) -> list:
    files = []
    for ext in VALID_EXTENSIONS:
        files.extend(glob.glob(os.path.join(post_dir, f"*{ext}")))
        files.extend(glob.glob(os.path.join(post_dir, f"*{ext.upper()}")))
    return sorted(set(files))


def build_raw_url(repo: str, branch: str, path: str) -> str:
    clean = path.replace("\\", "/")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{clean}"


def create_carousel_item(acc_id: str, token: str, image_url: str) -> str:
    r = requests.post(
        f"{GRAPH_API}/{acc_id}/media",
        data={
            "image_url": image_url,
            "is_carousel_item": "true",
            "access_token": token,
        },
        timeout=30,
    ).json()

    if "error" in r:
        raise RuntimeError(f"Error creando item de carrusel: {r['error'].get('message', r)}")
    if "id" not in r:
        raise RuntimeError(f"Respuesta inesperada al crear item: {r}")

    return r["id"]


def create_carousel_container(acc_id: str, token: str, children: list, caption: str) -> str:
    r = requests.post(
        f"{GRAPH_API}/{acc_id}/media",
        data={
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "caption": caption,
            "access_token": token,
        },
        timeout=30,
    ).json()

    if "error" in r:
        raise RuntimeError(f"Error creando contenedor carrusel: {r['error'].get('message', r)}")
    if "id" not in r:
        raise RuntimeError(f"Respuesta inesperada al crear carrusel: {r}")

    return r["id"]


def wait_until_ready(creation_id: str, token: str, timeout: int = 120) -> bool:
    waited = 0
    while waited < timeout:
        r = requests.get(
            f"{GRAPH_API}/{creation_id}",
            params={"fields": "status_code", "access_token": token},
            timeout=15,
        ).json()
        status = r.get("status_code", "UNKNOWN")
        print(f"  Estado: {status} ({waited}s)")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            print(f"  Instagram reporto ERROR al procesar: {r}")
            return False
        time.sleep(5)
        waited += 5
    print(f"  Timeout: contenedor no listo en {timeout}s")
    return False


def publish():
    token = os.getenv("IG_ACCESS_TOKEN")
    acc_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
    post_dir_name = (os.getenv("POST_DIR") or "").strip()
    repo = os.getenv("REPO", "")
    branch = os.getenv("BRANCH", "main")

    missing = [name for name, val in [
        ("IG_ACCESS_TOKEN", token),
        ("INSTAGRAM_ACCOUNT_ID", acc_id),
        ("POST_DIR", post_dir_name),
    ] if not val]
    if missing:
        print(f"Error: faltan variables de entorno: {missing}")
        sys.exit(1)

    post_dir = os.path.join("posts", post_dir_name)
    if not os.path.isdir(post_dir):
        print(f"Error: no se encontro la carpeta '{post_dir}'")
        print(f"  Carpetas disponibles en posts/: {os.listdir('posts') if os.path.isdir('posts') else '(posts/ no existe)'}")
        sys.exit(1)

    caption_path = os.path.join(post_dir, "caption.txt")
    if not os.path.exists(caption_path):
        print(f"Error: no se encontro '{caption_path}'")
        sys.exit(1)
    with open(caption_path, encoding="utf-8") as f:
        caption = f.read().strip()

    image_files = get_image_files(post_dir)

    if len(image_files) < 2:
        print(f"Error: se necesitan minimo 2 imagenes para un carrusel (encontradas: {len(image_files)})")
        print(f"  Archivos en '{post_dir}': {os.listdir(post_dir)}")
        sys.exit(1)

    if len(image_files) > 10:
        print(f"Aviso: {len(image_files)} imagenes encontradas, usando solo las primeras 10 (limite de Instagram)")
        image_files = image_files[:10]

    print(f"\n{'='*55}")
    print(f"  PUBLICADOR DE CARRUSEL PETCOLINAS")
    print(f"{'='*55}")
    print(f"  Carpeta : posts/{post_dir_name}/")
    print(f"  Imagenes: {len(image_files)}")
    print(f"  Caption : {caption[:80]}{'...' if len(caption) > 80 else ''}")
    print()

    if repo:
        image_urls = [build_raw_url(repo, branch, f) for f in image_files]
    else:
        print("Aviso: REPO no definido — asegurate de correr esto desde GitHub Actions")
        image_urls = image_files

    # Paso 1: crear item containers
    print(f"[1/3] Creando {len(image_files)} items del carrusel...")
    child_ids = []
    for i, (img_file, img_url) in enumerate(zip(image_files, image_urls), 1):
        print(f"  [{i}/{len(image_files)}] {os.path.basename(img_file)}")
        item_id = create_carousel_item(acc_id, token, img_url)
        print(f"        item_id: {item_id}")
        child_ids.append(item_id)
        if i < len(image_files):
            time.sleep(1)

    # Paso 2: crear contenedor carrusel
    print(f"\n[2/3] Creando contenedor CAROUSEL ({len(child_ids)} items)...")
    carousel_id = create_carousel_container(acc_id, token, child_ids, caption)
    print(f"  carousel_id: {carousel_id}")

    # Paso 3: esperar status FINISHED
    print("\n[3/3] Esperando que Instagram procese el carrusel...")
    if not wait_until_ready(carousel_id, token):
        print("Error: el carrusel no quedo listo para publicar")
        sys.exit(1)

    # Paso 4: publicar
    print("  Publicando...")
    pub = requests.post(
        f"{GRAPH_API}/{acc_id}/media_publish",
        data={"creation_id": carousel_id, "access_token": token},
        timeout=30,
    ).json()

    if "error" in pub:
        print(f"Error de Meta API al publicar: {pub['error'].get('message', pub)}")
        sys.exit(1)

    print(f"\nCarrusel publicado en Instagram con exito! ID: {pub.get('id')}")


if __name__ == "__main__":
    publish()
