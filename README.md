# PetColinas — Publicador de Carruseles en Instagram

Publica carruseles de diseño en la cuenta de Instagram de PetColinas usando la Graph API de Meta. Las imágenes y el caption se preparan por fuera (Canva, Photoshop, etc.) y se colocan en una carpeta del repositorio. El bot solo lee esa carpeta y publica.

---

## Estructura del repositorio

```
posts/
  <nombre-del-post>/
    01.png          ← primera imagen del carrusel
    02.png          ← segunda imagen
    03.png          ← ...
    caption.txt     ← caption completo del post
  scheduled/        ← carpeta para publicaciones automáticas programadas
publish_carousel.py ← script de publicación (Graph API de Meta)
requirements.txt
.github/workflows/
  daily_content.yml ← workflow principal (manual + schedule)
```

---

## Cómo agregar un post nuevo

1. **Diseña el carrusel** en Canva, Photoshop u otra herramienta.

2. **Exporta las imágenes** como archivos ordenados alfabéticamente:
   ```
   01.png   02.png   03.png   ...
   ```
   - Mínimo **2 imágenes**, máximo **10** (límite de Instagram).
   - Formatos aceptados: `.png`, `.jpg`, `.jpeg`.
   - Resolución recomendada: **1080×1080 px** (cuadrado).

3. **Crea la carpeta** del post dentro de `posts/`:
   ```
   posts/
     mi-post-del-lunes/
       01.png
       02.png
       03.png
       caption.txt
   ```

4. **Escribe el caption** en `caption.txt` (máx. 2200 caracteres para Instagram).

5. **Haz commit y push** al repositorio (rama `main`):
   ```bash
   git add posts/mi-post-del-lunes/
   git commit -m "Agrega carrusel: mi-post-del-lunes"
   git push origin main
   ```

---

## Cómo publicar manualmente

1. Ve al repositorio en GitHub.
2. Haz clic en **Actions** → **PetColinas — Publicar Carrusel**.
3. Haz clic en **Run workflow**.
4. En el campo **"Carpeta del carrusel en posts/"**, escribe el nombre de tu carpeta (ej: `mi-post-del-lunes`).
5. Haz clic en **Run workflow**.

El workflow tomará las imágenes del repositorio, las servirá como URLs públicas de GitHub y las publicará como carrusel en Instagram.

---

## Publicación automática (schedule)

El schedule viene **comentado** en el workflow. Para activarlo:

1. Edita `.github/workflows/daily_content.yml`.
2. Descomenta el bloque `schedule`:
   ```yaml
   schedule:
     - cron: '0 13 * * 0,1,3,4,5,6'
   ```
3. Coloca las imágenes y el caption del día en la carpeta `posts/scheduled/` antes de la hora programada.
4. El bot publicará esa carpeta automáticamente.

> **Horario:** 9:00 AM hora República Dominicana (UTC−4) = 13:00 UTC. Se ejecuta todos los días excepto martes (PetColinas está cerrado).

---

## Secrets de GitHub requeridos

| Secret | Descripción |
|---|---|
| `IG_ACCESS_TOKEN` | Token de acceso de Meta (Page Access Token) |
| `INSTAGRAM_ACCOUNT_ID` | ID numérico de la cuenta de Instagram Business |

Configúralos en **Settings → Secrets and variables → Actions** del repositorio.

---

## Dry run (prueba sin publicar)

Para verificar que el script encuentra las imágenes y el caption correctamente sin llamar a la API de Meta, corre localmente:

```bash
# Simula las variables de entorno del workflow (sin tokens reales)
POST_DIR=ejemplo REPO=victorbeltre/ig-de-petcolinas- BRANCH=main python publish_carousel.py
```

El script fallará al intentar crear los contenedores en Meta (por falta del token), pero antes imprimirá las imágenes encontradas y el caption, confirmando que la lectura de la carpeta es correcta.

---

## Archivos desactivados

Los siguientes archivos son legado del flujo anterior (generación con IA) y están desactivados (`.disabled`). No se ejecutan en ningún workflow:

- `generate_content.py.disabled` — generaba imagen con Stable Horde y caption con Claude (Anthropic).
- `gemini_trigger.py.disabled` — subía imágenes a GitHub y disparaba workflows vía Personal Access Token.
- `.github/workflows/run_bot.yml.disabled` — workflow alternativo del flujo anterior.

Puedes eliminarlos si ya no los necesitas.
