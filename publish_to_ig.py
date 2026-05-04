import os
import sys
import requests


def publish():
    token = os.getenv("IG_ACCESS_TOKEN")
    acc_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
    img_url = os.getenv("IMAGE_URL")
    caption = os.getenv("CAPTION")

    missing = [v for v, k in [("IG_ACCESS_TOKEN", token), ("INSTAGRAM_ACCOUNT_ID", acc_id), ("IMAGE_URL", img_url), ("CAPTION", caption)] if not k]
    if missing:
        print(f"Error: faltan variables de entorno: {missing}")
        sys.exit(1)

    print(f"Creando contenedor para imagen: {img_url[:60]}...")

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

    pub = requests.post(
        f"https://graph.facebook.com/v19.0/{acc_id}/media_publish",
        data={"creation_id": creation_id, "access_token": token},
    ).json()

    if "error" in pub:
        print(f"Error de Meta API al publicar: {pub['error'].get('message', pub)}")
        sys.exit(1)

    print(f"Post publicado en Instagram con exito! ID del post: {pub.get('id')}")


if __name__ == "__main__":
    publish()
