# Plugin: petcolinas-image

Genera imagenes y **afiches de marca PetColinas** con Google Imagen 4 desde
cualquier conversacion de Claude (incluido Claude Cowork), usando **GitHub como
puente**: la API key vive en los Secrets del repo, nunca en tu maquina.

Incluye la skill `google-image` con dos modos:
- **Imagen normal**: una foto a partir de un prompt.
- **Afiche de marca**: fondo de Imagen 4 + logo, colores y texto exacto de PetColinas.

## Instalar en Claude Cowork / app de escritorio
1. Abre **Customize** (o el boton `+`) → **Plugins / Add plugin**.
2. Agrega el marketplace por URL del repo:
   `https://github.com/victorbeltre/IG-De-Petcolinas-`
3. Instala el plugin **petcolinas-image**.
4. Listo: en cualquier conversacion podras pedir imagenes/afiches.

## Instalar en Claude Code (CLI)
```bash
/plugin marketplace add victorbeltre/IG-De-Petcolinas-
/plugin install petcolinas-image@petcolinas
```

## Requisitos
- `git` con acceso de **push** al repo del puente (tu login de GitHub).
- El secret **`GOOGLE_AI_KEY`** configurado en los Secrets del repo (ya lo tienes).
- **Ninguna** API key en tu maquina.

## Uso
- "Genera una foto de un perro corriendo en la playa"
- "Hazme un afiche PetColinas de descuento en banos, con el WhatsApp"

La skill se encarga del resto: sube el pedido, GitHub genera con Imagen 4 y
devuelve la imagen.

> La logica de generacion (workflow + scripts) vive en la rama `main` del repo:
> `.github/workflows/generar_imagen.yml`, `.github/scripts/bridge_generate.py`
> y `.github/scripts/bridge_afiche.py`.
