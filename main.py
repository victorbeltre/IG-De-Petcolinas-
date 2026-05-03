import os
import requests

ACCESS_TOKEN = os.getenv('IG_ACCESS_TOKEN')
INSTAGRAM_ACCOUNT_ID = os.getenv('INSTAGRAM_ACCOUNT_ID')

# Imagen real de perritos bañándose para la prueba
IMAGE_URL = 'https://images.unsplash.com/photo-1516734212186-a967f81ad0d7?q=80&w=1080&auto=format&fit=crop'
CAPTION = (
    "¡Día de mimos en PetColinas! 🐾 ¿Sabías que un buen baño no solo los pone bellos, "
    "sino que cuida su salud? 🐶✨ ¡Trae a tu mejor amigo hoy! \n\n"
    "📱 809-752-6806 | 📍 Plaza Las Colinas #PetColinas #GroomingRD"
)

def publicar():
    if not ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        print("Error: Revisa tus Secrets en GitHub.")
        return

    url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {'image_url': IMAGE_URL, 'caption': CAPTION, 'access_token': ACCESS_TOKEN}
    res = requests.post(url, data=payload).json()
    
    if 'id' in res:
        creation_id = res['id']
        url_pub = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        requests.post(url_pub, data={'creation_id': creation_id, 'access_token': ACCESS_TOKEN})
        print("¡LOGRADO! Revisa el Instagram de PetColinas 🚀")
    else:
        print("Error de Meta:", res)

if __name__ == "__main__":
    publicar()
