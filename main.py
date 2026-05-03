import os
import requests
import google.generativeai as genai
import random

# CONFIGURACIÓN DESDE GITHUB SECRETS
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
IG_TOKEN = os.getenv('IG_ACCESS_TOKEN')
IG_ID = os.getenv('INSTAGRAM_ACCOUNT_ID')

# CONFIGURAR GEMINI CON TU IDENTIDAD DE GEMA
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

PROMPT_SISTEMA = """
Eres el Creador de Contenido Oficial de PetColinas, una veterinaria y peluquería canina en Santo Domingo Oeste.
DATOS CLAVE:
- WhatsApp: 809-752-6806 | Instagram: @petcolinas
- Ubicación: Plaza De Las Colinas, Av. Prolongación 27 de Febrero.
- Tono: Cercano, cálido, emotivo, español dominicano natural y auténtico.
- Estructura: Gancho, Cuerpo con beneficio, Llamado a la acción, Datos de contacto y Hashtags.

TAREA: Genera un post de Instagram humano y profesional. Puede ser un tip educativo, una promoción de grooming o un mensaje sobre el cuidado de mascotas. No menciones que eres una IA. Solo entrega el texto del caption.
"""

def generar_contenido():
    try:
        response = model.generate_content(PROMPT_SISTEMA)
        caption = response.text
        
        # Selección de imagen aleatoria de alta calidad sobre mascotas
        temas_visuales = ["dog-grooming", "happy-dog", "veterinarian-pet", "cute-puppy"]
        foto_tema = random.choice(temas_visuales)
        # LoremFlickr nos da una imagen fresca cada vez
        image_url = f"https://loremflickr.com/1080/1080/{foto_tema}/all"
        
        return caption, image_url
    except Exception as e:
        print(f"Error generando contenido: {e}")
        return None, None

def publicar_instagram(caption, image_url):
    # 1. Crear contenedor de media
    url_media = f"https://graph.facebook.com/v18.0/{IG_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': IG_TOKEN
    }
    r = requests.post(url_media, data=payload).json()
    
    if 'id' in r:
        creation_id = r['id']
        # 2. Publicar oficialmente
        url_pub = f"https://graph.facebook.com/v18.0/{IG_ID}/media_publish"
        requests.post(url_pub, data={'creation_id': creation_id, 'access_token': IG_TOKEN})
        print("¡ÉXITO! Post con identidad de Gema publicado en @petcolinas. 🐾")
    else:
        print(f"Error al subir a Instagram: {r}")

if __name__ == "__main__":
    texto, foto = generar_contenido()
    if texto and foto:
        publicar_instagram(texto, foto)
