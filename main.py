import os
import requests
import google.generativeai as genai

# Configuración de llaves
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
IG_TOKEN = os.getenv('IG_ACCESS_TOKEN')
IG_ID = os.getenv('INSTAGRAM_ACCOUNT_ID')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def generar_contenido():
    prompt = (
        "Eres el community manager de PetColinas, una veterinaria y grooming en RD. "
        "Escribe un caption de Instagram humano, cálido y profesional sobre un tip de salud canina. "
        "No menciones que eres una IA. Solo dame el texto y al final una URL de imagen de Unsplash "
        "relacionada con perros (puedes usar https://source.unsplash.com/1080x1080/?dog,salud)."
    )
    respuesta = model.generate_content(prompt)
    # Aquí el script separa el texto de la imagen (simplificado)
    return respuesta.text

def publicar(texto, imagen):
    url = f"https://graph.facebook.com/v18.0/{IG_ID}/media"
    payload = {'image_url': imagen, 'caption': texto, 'access_token': IG_TOKEN}
    res = requests.post(url, data=payload).json()
    if 'id' in res:
        creation_id = res['id']
        url_pub = f"https://graph.facebook.com/v18.0/{IG_ID}/media_publish"
        requests.post(url_pub, data={'creation_id': creation_id, 'access_token': IG_TOKEN})
        print("¡Contenido generado por IA publicado!")

if __name__ == "__main__":
    # Este flujo ahora es inteligente
    contenido = generar_contenido()
    # (Lógica para separar URL y texto)
    # publicar(texto, url)
