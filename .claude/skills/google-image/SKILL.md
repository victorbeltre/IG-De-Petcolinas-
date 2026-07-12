---
name: google-image
description: >
  Genera imagenes reales con el generador de Google Imagen 4 (Google AI Studio)
  a partir de un prompt de texto. Usar SIEMPRE que el usuario pida crear, generar,
  hacer o disenar una imagen, foto, afiche, anuncio, poster, logo o grafico con
  Google, Gemini o Imagen — en cualquier proyecto o conversacion, incluido Claude
  Cowork. Tambien sirve para generar fondos o piezas para redes sociales. Requiere
  la variable de entorno GOOGLE_AI_KEY (o el archivo ~/.google_ai_key).
---

# Google Image (Imagen 4)

Genera imagenes con el modelo Google Imagen 4 usando la API de Google AI Studio.

## Cuando usar esta skill
- El usuario pide "genera/crea/hazme una imagen/foto/afiche/anuncio con Google/Gemini/Imagen".
- Se necesita una imagen real (no un placeholder) para un post, anuncio, portada, etc.
- Funciona en cualquier carpeta o proyecto y en Claude Cowork.

## Requisito unico: la API key
El script necesita la API key de Google AI Studio en:
- la variable de entorno `GOOGLE_AI_KEY`, **o**
- el archivo `~/.google_ai_key` (solo la key adentro, sin comillas).

La key **nunca** se imprime en logs. Si falta, el script lo avisa con instrucciones.
NUNCA muestres ni publiques el valor de la key; refierete a ella solo por su nombre.

## Como ejecutarla
El script vive junto a este archivo: `generate_image.py`. Requiere `requests`
(`pip install requests` si no esta).

Ejemplos:
```bash
# Imagen simple 1:1
python generate_image.py "un golden retriever feliz en un parque, luz natural, alta calidad" --out perro.png

# Afiche cuadrado para redes (con texto incluido en el prompt)
python generate_image.py "Afiche cuadrado de oferta de empleo veterinario, fondo verde, texto 'ESTAMOS CONTRATANDO', estilo moderno y profesional, sin marcas de agua" --out anuncio.png

# Varias variaciones a la vez
python generate_image.py "gato naranja jugando, fondo claro" --n 4 --out gato.png

# Formato vertical para historias
python generate_image.py "clinica veterinaria moderna y luminosa" --aspect 9:16 --out historia.png

# Maxima calidad
python generate_image.py "logo minimalista de una huella de perro" --model ultra --out logo.png
```

### Parametros
- `--out` archivo de salida (default `image.png`). Con `--n > 1` se guardan como `nombre_1.png`, `nombre_2.png`, ...
- `--n` cantidad de imagenes, 1 a 4 (default 1).
- `--aspect` `1:1`, `3:4`, `4:3`, `9:16`, `16:9` (default `1:1`).
- `--model` `fast` (rapido/barato), `standard` (default), `ultra` (mejor calidad).
- `--no-people` evita generar personas.

## Buenas practicas de prompt
- Describe sujeto, entorno, iluminacion y estilo. Termina con "alta calidad, sin marcas de agua".
- Para texto dentro de la imagen, escribe el texto EXACTO entre comillas en el prompt y revisa el resultado (los modelos a veces escriben mal; regenera si hace falta).
- Para fotos realistas usa `--model standard` o `ultra`; para bocetos rapidos `--model fast`.

## Despues de generar
1. Confirma la ruta del archivo generado.
2. Muestra la imagen al usuario (adjunta el archivo) para que la revise.
3. Si no le gusta, ajusta el prompt y vuelve a generar.

## Nota de seguridad
La key se lee del entorno o de un archivo local y viaja en un header HTTP,
nunca en la URL. No la imprimas, no la escribas en archivos versionados,
ni la incluyas en commits.
