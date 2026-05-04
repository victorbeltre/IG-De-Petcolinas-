import os
import sys
import time
import requests


def wait_until_ready(acc_id: str, creation_id: str, token: str, timeout: int = 90) -> bool:
    """Espera hasta que Instagram termine de procesar el contenedor."""
    url = f"https://graph.facebook.com/v19.0/{creation_id}"
    waited = 0
    while waited < timeout:
        r = requests.get(url, params={"fields": "status_code", "access_token": token}).json()
        status = r.get("status_code", "UNKNOWN")
        print(f"  Estado del contenedor: {status} ({waited}s)")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            print(f"  Instagram reporto ERROR al procesar la imagen: {r}")
            return False
        time.sleep(5)
        waited += 5
    print(f"  Timeout: el contenedor no estuvo listo en {timeout}s")
    return False


def publish():
    token = os.getenv("IG_ACCESS_TOKEN")
    acc_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
    img_url = os.getenv("IMAGE_URL")
    caption = os.getenv("CAPTION")

    missing = [name for name, val in [
        ("IG_ACCESS_TOKEN", token),
        ("INSTAGRAM_ACCOUNT_ID", acc_id),
        ("IMAGE_URL", img_url),
        ("CAPTION", caption),
    ] if not val]
    if missing:
        print(f"Error: faltan variables de entorno: {missing}")
        sys.exit(1)

    print(f"Creando contenedor para imagen: {img_url[:60]}...")

    # Paso 1: Crear contenedor
    r = requests.post(
        f"https://graph.facebook.com/v19.0/{acc_id}/media",
        data={"image_url": img_url, "caption": caption, "access_token": token},
    ).json()

    if "error" in r:
        print(f"Error de Meta API al crear contenedor: {r['error'].get('message', r)}")
        sys.exit(1)

    if "id" not in r:
        print(f"Respuesta inesperada de Meta: {r}")
        sys.exit(1)

    creation_id = r["id"]
    print(f"Contenedor creado con ID: {creation_id}")

    # Paso 2: Esperar a que Instagram procese la imagen
    print("Esperando que Instagram procese la imagen...")
    if not wait_until_ready(acc_id, creation_id, token):
        print("Error: el contenedor no quedo listo para publicar")
        sys.exit(1)

    # Paso 3: Publicar
    print("Publicando...")
    pub = requests.post(
        f"https://graph.facebook.com/v19.0/{acc_id}/media_publish",
        data={"creation_id": creation_id, "access_token": token},
    ).json()

    if "error" in pub:
        print(f"Error de Meta API al publicar: {pub['error'].get('message', pub)}")
        sys.exit(1)

    print(f"Post publicado en Instagram con exito! ID: {pub.get('id')}")


if __name__ == "__main__":
    publish()
