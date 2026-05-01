import os
import requests

# Datos desde los Secrets de GitHub
ACCESS_TOKEN = os.getenv('IG_ACCESS_TOKEN')
INSTAGRAM_ACCOUNT_ID = os.getenv('INSTAGRAM_ACCOUNT_ID')

# CONTENIDO (Última imagen generada)
IMAGE_URL = 'https://raw.githubusercontent.com/google-gemini/petcolinas/main/image_baño.jpg' 
CAPTION = (
    "¡Papá y mamá de peludos! 🐾 ¿Sabían que no todos los perros se bañan con la misma frecuencia? "
    "La salud de su piel es vital para que estén felices y activos. 🐶✨\n\n"
    "Aquí en PetColinas cuidamos cada detalle para que tu mejor amigo salga oliendo a gloria y con el pelo impecable. "
    "¡Agenda su cita hoy mismo!\n\n"
    "📱 809-752-6806 | 📍 Plaza Las Colinas\n\n"
    "#PetColinas #GroomingRD #VeterinariaRD #MascotasRD #SantoDomingoOeste"
)

def publicar():
    if not ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        print("Error: Faltan Secrets.")
        return

    # Paso 1: Subir media
    url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {'image_url': IMAGE_URL, 'caption': CAPTION, 'access_token': ACCESS_TOKEN}
    res = requests.post(url, data=payload).json()
    
    if 'id' in res:
        # Paso 2: Publicar
        creation_id = res['id']
        url_pub = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        res_pub = requests.post(url_pub, data={'creation_id': creation_id, 'access_token': ACCESS_TOKEN})
        print("¡Publicado en Instagram! 🐾")
    else:
        print("Error:", res)

if __name__ == "__main__":
    publicar()
