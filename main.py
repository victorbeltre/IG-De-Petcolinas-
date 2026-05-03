import os
import requests
import google.generativeai as genai
import random

# CONFIGURACIÓN DE LLAVES
# Google prefiere GOOGLE_API_KEY por defecto
api_key = os.getenv('GOOGLE_API_KEY')
IG_TOKEN = os.getenv('IG_ACCESS_TOKEN')
IG_ID = os.getenv('INSTAGRAM_ACCOUNT_ID')

# CONFIGURAR GEMINI
if api_key:
    genai.configure(api_key=api_key)
else:
    print("Error: No se encontró la API Key en los secretos de GitHub")

model = genai.GenerativeModel('gemini-1.5-flash')

PROMPT_SISTEMA = """
Eres el Creador de Contenido Oficial de PetColinas, una veterinaria y peluquería canina en Santo Domingo Oeste.
DATOS: WhatsApp 809-752-6806, Instagram @petcolinas, Ubicación: Plaza De Las Colinas.
TONO: Cercano, cálido, emotivo, español dominicano natural.
TAREA: Genera un post de Instagram humano sobre salud o grooming. Solo entrega el texto del caption.
"""

def generar_contenido():
    try:
        response = model.generate_content(PROMPT_SISTEMA)
        caption = response.text
        
        # Imagen aleatoria de mascotas
        temas = ["dog", "puppy", "veterinarian", "grooming"]
        image_url = f"https://loremflickr.com/1080/1080/{random.choice(temas)}/all"
        
        return caption, image_url
    except Exception as e:
        print(f"Error en Gemini: {e}")
        return None, None

def publicar_en_ig(caption, image_url):
    url_media = f"https://graph.facebook.com/v18.0/{IG_ID}/media"
    payload = {'image_url': image_url, 'caption': caption, 'access_token': IG_TOKEN}
    res = requests.post(url_media, data=payload).json()
    
    if 'id' in res:
        creation_id = res['id']
        url_pub = f"https://graph.facebook.com/v18.0/{IG_ID}/media_publish"
        requests.post(url_pub, data={'creation_id': creation_id, 'access_token': IG_TOKEN})
        print("¡LOGRADO! Post de PetColinas publicado con éxito. 🐾")
    else:
        print(f"Error de Meta: {res}")

if __name__ == "__main__":
    if api_key and IG_TOKEN and IG_ID:
        texto, foto = generar_contenido()
        if texto and foto:
            publicar_en_ig(texto, foto)
    else:
        print("Faltan variables de entorno. Revisa tus GitHub Secrets.")
