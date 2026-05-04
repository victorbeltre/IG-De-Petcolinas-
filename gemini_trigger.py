"""
Script para que la Gema de Gemini dispare el workflow de Instagram en GitHub.

Uso:
    python gemini_trigger.py <image_url> <caption>

O importado desde tu Gema de Gemini:
    from gemini_trigger import trigger_instagram_post
    trigger_instagram_post(image_url="https://...", caption="...")

Variables de entorno necesarias:
    GITHUB_PAT  -> Personal Access Token de GitHub con permiso 'repo'
"""

import os
import sys
import requests

GITHUB_OWNER = "victorbeltre"
GITHUB_REPO = "ig-de-petcolinas-"
EVENT_TYPE = "publicar_post_gemini"


def trigger_instagram_post(image_url: str, caption: str) -> bool:
    pat = os.getenv("GITHUB_PAT")
    if not pat:
        print("Error: falta la variable de entorno GITHUB_PAT")
        return False

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/dispatches"

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {pat}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={
            "event_type": EVENT_TYPE,
            "client_payload": {
                "image_url": image_url,
                "caption": caption,
            },
        },
    )

    if response.status_code == 204:
        print("Workflow de Instagram disparado con exito en GitHub Actions.")
        return True
    else:
        print(f"Error al disparar el workflow: {response.status_code} {response.text}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python gemini_trigger.py <image_url> <caption>")
        sys.exit(1)

    success = trigger_instagram_post(image_url=sys.argv[1], caption=sys.argv[2])
    sys.exit(0 if success else 1)
