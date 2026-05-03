import os
import requests
import random
import google.generativeai as genai

# CONFIGURACIÓN DE LLAVES
api_key = os.getenv('GOOGLE_API_KEY')
IG_TOKEN = os.getenv('IG_ACCESS_TOKEN')
IG_ID = os.getenv('INSTAGRAM_ACCOUNT_ID')

def generar_contenido():
    if not api_key:
        print("Error: No se encontró GOOGLE_API_KEY")
        return None, None
        
    try:
        genai.configure(api_key=api_key)
        
        # USANDO GEMINI 3 FLASH (NANO BANANA 2)
        # El nombre técnico en la API es gemini-2.0-flash
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = """
        Eres el Creador de Contenido Oficial de PetColinas en Santo Domingo Oeste. 
        Datos: WhatsApp 809-752-6806, Instagram @petcolinas.
        Tono: Dominicano, cálido, profesional y auténtico. 
        Tarea: Crea un post de Instagram sobre salud o higiene de mascotas (tip de grooming o veterinaria). 
        Solo devuelve el texto del caption listo para publicar. Sin notas ni títulos.
        """
        
        response = model.generate_content(prompt)
        caption = response.text
        
        # Imagen aleatoria de mascotas
        temas = ["dog", "puppy", "veterinarian", "grooming"]
        image_url = f"https://loremflickr.com/1080/1080/{random.choice(temas)}/all"
        
        return caption, image_url
    except Exception as e:
        print(f"Error en Gemini (Nano Banana): {e}")
        return None, None

def publicar_en_ig(caption, image_url):
    url_media = f"https://graph.facebook.com/v18.0/{IG_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': IG_TOKEN
    }
    res = requests.post(url_media, data=payload).json()
    
    if 'id' in res:
        creation_id = res['id']
        url_pub = f"https://graph.facebook.com/v18.0/{IG_ID}/media_publish"
        requests.post(url_pub, data={'creation_id': creation_id, 'access_token': IG_TOKEN})
        print("¡LOGRADO! Post generado por Nano Banana ya está en Instagram. 🐾🍌")
    else:
        print(f"Error de Meta: {res}")

if __name__ == "__main__":
    if all([api_key, IG_TOKEN, IG_ID]):
        texto, foto = generar_contenido()
        if texto and foto:
            publicar_en_ig(texto, foto)
    else:
        print("Faltan variables de entorno en Secrets.")
