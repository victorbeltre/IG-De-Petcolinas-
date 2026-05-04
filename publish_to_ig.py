import os
import requests
import sys

def publish():
    token = os.getenv("IG_ACCESS_TOKEN")
    acc_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
    img_url = os.getenv("IMAGE_URL")
    caption = os.getenv("CAPTION")

    if not img_url or not caption:
        print("Error: No se recibió imagen o caption de Gemini.")
        sys.exit(1)

    # Paso 1: Crear el contenedor del media
    post_url = f"https://graph.facebook.com/v19.0/{acc_id}/media"
    payload = {
        'image_url': img_url,
        'caption': caption,
        'access_token': token
    }
    
    r = requests.post(post_url, data=payload)
    result = r.json()
    
    if 'id' not in result:
        print(f"Error creando contenedor: {result}")
        sys.exit(1)

    creation_id = result['id']

    # Paso 2: Publicar el contenedor
    publish_url = f"https://graph.facebook.com/v19.0/{acc_id}/media_publish"
    publish_payload = {
        'creation_id': creation_id,
        'access_token': token
    }
    
    r_pub = requests.post(publish_url, data=publish_payload)
    print(f"Resultado final: {r_pub.json()}")

if __name__ == "__main__":
    publish()
