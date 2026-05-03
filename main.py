import os
import requests
import google.generativeai as genai
import random

# CONFIGURACIÓN DE LLAVES
api_key = os.getenv('GOOGLE_API_KEY')
IG_TOKEN = os.getenv('IG_ACCESS_TOKEN')
IG_ID = os.getenv('INSTAGRAM_ACCOUNT_ID')

def generar_contenido():
    if not api_key:
        print("Error: No se encontró la llave GOOGLE_API_KEY")
        return None, None
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = """
    Eres el Creador de Contenido Oficial de PetColinas, una veterinaria y peluquería canina en Santo Domingo Oeste.
    DATOS: WhatsApp 809-752-6806, Instagram @petcolinas.
    TONO: Cercano, cálido, emotivo, español dominicano natural.
    TAREA: Genera un post de Instagram humano sobre salud o grooming. Solo entrega el texto del caption listo para publicar.
    """
    
    try:
        response = model.generate_content(prompt)
        caption = response.text
        # Seleccionamos una imagen aleatoria de perritos/gatos
        temas = ["dog", "puppy", "cat", "veterinarian", "pet-grooming"]
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
    if IG_TOKEN and IG_ID and api_key:
        texto, foto = generar_contenido()
        if texto and foto:
            publicar_en_ig(texto, foto)
    else:
        print("Faltan variables de entorno. Revisa GEMINI_API_KEY, IG_ACCESS_TOKEN e INSTAGRAM_ACCOUNT_ID en GitHub Secrets.")
