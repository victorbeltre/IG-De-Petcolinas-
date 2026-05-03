import os
import requests
import google.generativeai as genai
import random

# CONFIGURACIÓN
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
IG_TOKEN = os.getenv('IG_ACCESS_TOKEN')
IG_ID = os.getenv('INSTAGRAM_ACCOUNT_ID')

# CONFIGURAR GEMINI CON IDENTIDAD DE TU GEMA
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

PROMPT_SISTEMA = """
Eres el Creador de Contenido Oficial de PetColinas, una veterinaria y peluquería canina en Santo Domingo Oeste.
DATOS CLAVE:
- WhatsApp: 809-752-6806 | Instagram: @petcolinas
- Ubicación: Plaza De Las Colinas, Av. Prolongación 27 de Febrero.
- Tono: Cercano, cálido, emotivo, español dominicano natural y auténtico. No rígido.
- Estructura: Gancho, Cuerpo con beneficio, Llamado a la acción (CTA), Datos de contacto y Hashtags.

TAREA: Genera un post de Instagram humano. Puede ser un tip de salud, promo de grooming o mensaje de amor a las mascotas. 
No menciones que eres una IA. Solo entrega el texto del caption listo para copiar.
"""

def generar_contenido():
    try:
        response = model.generate_content(PROMPT_SISTEMA)
        caption = response.text
        
        # Selección de imagen aleatoria profesional
        temas = ["dog", "puppy", "veterinarian", "dog-grooming"]
        tema = random.choice(temas)
        image_url = f"https://loremflickr.com/1080/1080/{tema}/all"
        
        return caption, image_url
    except Exception as e:
        print(f"Error en Gemini: {e}")
        return None, None

def publicar_en_ig(caption, image_url):
    url_media = f"https://graph.facebook.com/v18.0/{IG_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': IG_TOKEN
    }
    r = requests.post(url_media, data=payload).json()
    
    if 'id' in r:
        creation_id = r['id']
        url_pub = f"https://graph.facebook.com/v18.0/{IG_ID}/media_publish"
        requests.post(url_pub, data={'creation_id': creation_id, 'access_token': IG_TOKEN})
        print("¡LOGRADO! Post con estilo de Gema publicado. 🐾")
    else:
        print(f"Error de Meta: {r}")

if __name__ == "__main__":
    texto, foto = generar_contenido()
    if texto and foto:
        publicar_en_ig(texto, foto)
