import os
import requests

def publish():
    token = os.getenv('IG_ACCESS_TOKEN')
    acc_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
    img = os.getenv('IMAGE_URL')
    cap = os.getenv('CAPTION')

    # Paso 1: Crear contenedor
    url_media = f"https://graph.facebook.com/v19.0/{acc_id}/media"
    r = requests.post(url_media, data={
        'image_url': img,
        'caption': cap,
        'access_token': token
    }).json()

    if 'id' in r:
        creation_id = r['id']
        # Paso 2: Publicar
        url_pub = f"https://graph.facebook.com/v19.0/{acc_id}/media_publish"
        requests.post(url_pub, data={
            'creation_id': creation_id,
            'access_token': token
        })
        print("¡Post publicado en Instagram con éxito! 🐾")
    else:
        print(f"Error de Meta: {r}")
        exit(1)

if __name__ == "__main__":
    publish()
