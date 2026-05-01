import os
import requests

ACCESS_TOKEN = os.getenv('IG_ACCESS_TOKEN')
INSTAGRAM_ACCOUNT_ID = os.getenv('INSTAGRAM_ACCOUNT_ID')

# Imagen de prueba real (Un perrito feliz)
IMAGE_URL = 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=1080&q=80'
CAPTION = "¡Día de mimos en PetColinas! 🐾 Porque tu mejor amigo merece lo mejor. 🐶✨ 📱 809-752-6806 | 📍 Plaza Las Colinas #PetColinas #GroomingRD"

def publicar():
    url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {'image_url': IMAGE_URL, 'caption': CAPTION, 'access_token': ACCESS_TOKEN}
    res = requests.post(url, data=payload).json()
    
    if 'id' in res:
        creation_id = res['id']
        url_pub = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        requests.post(url_pub, data={'creation_id': creation_id, 'access_token': ACCESS_TOKEN})
        print("¡LOGRADO! Mira el Instagram de PetColinas 🚀")
    else:
        print("Error:", res)

if __name__ == "__main__":
    publicar()
