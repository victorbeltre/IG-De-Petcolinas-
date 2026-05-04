"""
Flujo completo de publicacion automatica PetColinas:
  1. Sube la imagen al repo de GitHub (carpeta raiz, archivo post_del_dia.jpg)
  2. Espera a que el CDN de GitHub propague la imagen
  3. Dispara el workflow de GitHub Actions para publicar en Instagram

Uso desde linea de comandos:
    python gemini_trigger.py <ruta_imagen.jpg> "<caption>"

Uso como modulo (desde tu script de Gemini):
    from gemini_trigger import upload_image_and_publish
    upload_image_and_publish("imagen.jpg", "Caption del post...")

Variable de entorno requerida:
    GITHUB_PAT -> Personal Access Token con permisos: repo, workflow
"""

import os
import sys
import base64
import time
import requests

GITHUB_OWNER = "victorbeltre"
GITHUB_REPO = "ig-de-petcolinas-"
GITHUB_BRANCH = "main"
IMAGE_FILENAME = "post_del_dia.jpg"
EVENT_TYPE = "publicar_post_gemini"
RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}"


def _auth_headers():
    pat = os.getenv("GITHUB_PAT")
    if not pat:
        raise EnvironmentError("Falta la variable de entorno GITHUB_PAT")
    return {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def upload_image_to_github(image_path: str) -> str:
    """Sube la imagen al repo de GitHub y retorna su URL raw publica."""
    print(f"[1/3] Leyendo imagen: {image_path}")
    with open(image_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()

    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{IMAGE_FILENAME}"
    headers = _auth_headers()

    # Si el archivo ya existe necesitamos su SHA para poder actualizarlo
    existing = requests.get(api_url, headers=headers).json()
    sha = existing.get("sha")

    payload = {
        "message": f"Post automatico PetColinas {time.strftime('%Y-%m-%d')}",
        "content": content_b64,
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    response = requests.put(api_url, headers=headers, json=payload)

    if response.status_code in (200, 201):
        raw_url = f"{RAW_BASE}/{IMAGE_FILENAME}"
        print(f"[1/3] Imagen subida con exito: {raw_url}")
        return raw_url

    raise Exception(
        f"Error al subir imagen a GitHub: {response.status_code}\n{response.text}"
    )


def trigger_instagram_post(image_url: str, caption: str) -> bool:
    """Dispara el workflow de GitHub Actions con la URL de imagen y caption."""
    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/dispatches"

    response = requests.post(
        api_url,
        headers=_auth_headers(),
        json={
            "event_type": EVENT_TYPE,
            "client_payload": {
                "image_url": image_url,
                "caption": caption,
            },
        },
    )

    if response.status_code == 204:
        print("[3/3] Workflow de Instagram disparado con exito en GitHub Actions.")
        return True

    print(f"[3/3] Error al disparar el workflow: {response.status_code}\n{response.text}")
    return False


def upload_image_and_publish(image_path: str, caption: str, cdn_wait: int = 20) -> bool:
    """
    Flujo completo:
      1. Sube la imagen a GitHub
      2. Espera propagacion del CDN
      3. Dispara el workflow de Instagram
    """
    raw_url = upload_image_to_github(image_path)

    print(f"[2/3] Esperando {cdn_wait}s para que el CDN de GitHub propague la imagen...")
    time.sleep(cdn_wait)

    return trigger_instagram_post(raw_url, caption)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python gemini_trigger.py <ruta_imagen.jpg> \"<caption>\"")
        sys.exit(1)

    image_path_arg = sys.argv[1]
    caption_arg = sys.argv[2]

    if not os.path.exists(image_path_arg):
        print(f"Error: no se encontro la imagen: {image_path_arg}")
        sys.exit(1)

    success = upload_image_and_publish(image_path=image_path_arg, caption=caption_arg)
    sys.exit(0 if success else 1)
