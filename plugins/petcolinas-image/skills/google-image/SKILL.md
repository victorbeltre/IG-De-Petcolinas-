---
name: google-image
description: >
  Genera imagenes reales con Google Imagen 4 usando GitHub como puente (la API
  key vive en los Secrets del repo, NO en la maquina). Usar SIEMPRE que el
  usuario pida crear, generar, hacer o disenar una imagen, foto, afiche,
  anuncio, poster, logo o grafico con Google, Gemini o Imagen — en cualquier
  proyecto o conversacion, incluido Claude Cowork. Tambien sirve para fondos y
  piezas de redes sociales.
---

# Google Image (Imagen 4) — vía puente de GitHub

Genera imagenes con Google Imagen 4 **sin tener la API key en la maquina**.
La generacion corre en GitHub Actions, que ya tiene `GOOGLE_AI_KEY` en los
Secrets del repo. Tu solo pides; GitHub genera y devuelve la imagen.

## Cuando usar esta skill
- El usuario pide "genera/crea/hazme una imagen/foto/afiche/anuncio con Google/Gemini/Imagen".
- Se necesita una imagen real (no un placeholder) para un post, anuncio, portada, etc.
- Funciona en cualquier carpeta o proyecto y en Claude Cowork.

## Modo principal: el puente (recomendado)
Ejecuta el cliente `request_image.py`. Este:
1. Escribe un pedido y lo hace `push` al repo.
2. El push dispara el workflow que genera la imagen con Imagen 4.
3. Espera y baja la imagen resultante a la ruta que indiques.

```bash
# Imagen simple
python request_image.py "un golden retriever feliz en un parque, luz natural" --out perro.png

# Afiche cuadrado con texto (escribe el texto EXACTO entre comillas)
python request_image.py "Afiche cuadrado 'ESTAMOS CONTRATANDO', clinica veterinaria, estilo moderno, sin marcas de agua" --out anuncio.png

# Varias variaciones / vertical / maxima calidad
python request_image.py "gato naranja jugando" --n 4 --out gato.png
python request_image.py "clinica veterinaria luminosa" --aspect 9:16 --out historia.png
python request_image.py "logo huella de perro minimalista" --model ultra --out logo.png
```

### Parametros
- `--out` archivo de salida (default `image.png`). Con varias imagenes: `nombre_1.png`, `nombre_2.png`...
- `--n` cantidad 1-4 (default 1).
- `--aspect` `1:1`, `3:4`, `4:3`, `9:16`, `16:9` (default `1:1`).
- `--model` `fast`, `standard` (default), `ultra`.
- `--no-people` evita generar personas.

### Requisito
- `git` con acceso de push al repo del puente (config en `bridge.json`).
- **No** se necesita ninguna API key local.
- La primera vez clona el repo del puente en `~/.cache/imagen-bridge/` (solo
  archivos del repo, ningun secreto). Las siguientes veces reutiliza ese cache.

## Modo AFICHE de marca PetColinas
Para anuncios/afiches con la marca PetColinas automatica (logo real, colores
verde/naranja/dorado, texto EXACTO sin errores de IA). El fondo lo genera
Imagen 4 y la marca se compone encima.

Cuando el usuario pida "un afiche/anuncio de PetColinas de X", TU (Claude)
redactas los campos y llamas asi:

```bash
python request_image.py --afiche \
  --titulo "Baño y corte con 20% de descuento" \
  --subtitulo "Solo esta semana" \
  --punto "Baño desde RD$799" \
  --punto "Corte higiénico o completo" \
  --punto "Deslanado profesional" \
  --cta "WhatsApp: 809-752-6806" \
  --bg "perro pequeño recién bañado y peinado, luz suave, fondo limpio" \
  --out afiche.png
```

Campos del afiche:
- `--titulo` (obligatorio) titular corto y fuerte.
- `--subtitulo` (opcional) linea dorada de apoyo.
- `--punto` (repetible) vinetas; usa 3-5, cortas.
- `--cta` (opcional) barra naranja; para reclutar o vender pon el WhatsApp.
- `--bg` (opcional) descripcion del fondo (foto). Si se omite, usa un fondo de marca.

Guias:
- Precios: usa SOLO precios reales de PRECIOS_PETCOLINAS.json; no inventes.
- Manten el titulo a 2-4 palabras clave; el detalle va en las vinetas.
- El logo, los colores y el footer (@petcolinasrd) se ponen solos.

## Modo alterno: directo con key local
Si en algun entorno SI tienes la key (`GOOGLE_AI_KEY` en el entorno o
`~/.google_ai_key`), puedes generar sin GitHub con:
```bash
python generate_image.py "tu prompt" --out imagen.png
```

## Buenas practicas de prompt
- Describe sujeto, entorno, iluminacion y estilo. Cierra con "alta calidad, sin marcas de agua".
- Para texto dentro de la imagen, escribe el texto EXACTO entre comillas y revisa el resultado (regenera si sale mal).
- Fotos realistas: `--model standard` o `ultra`. Bocetos rapidos: `--model fast`.

## Despues de generar
1. Confirma la ruta del archivo generado.
2. Muestra la imagen al usuario para que la revise.
3. Si no le gusta, ajusta el prompt y vuelve a generar.

## Seguridad
La API key nunca esta en la maquina del usuario: vive en los Secrets de GitHub.
El workflow la usa en un header HTTP (no en la URL) y nunca la imprime. No la
pongas en archivos versionados ni en commits.
