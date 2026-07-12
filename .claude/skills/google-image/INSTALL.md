# Instalar la skill `google-image` (puente de GitHub)

Esta skill genera imagenes con Imagen 4 **usando GitHub como puente**: la API
key vive en los Secrets del repo, nunca en tu maquina.

## Requisitos del repo (una sola vez)
1. En el repo del puente debe existir el secret **`GOOGLE_AI_KEY`**
   (Settings → Secrets and variables → Actions). Ya lo tienes configurado.
2. Deben estar en la rama por defecto (`main`) estos archivos:
   - `.github/workflows/generar_imagen.yml`
   - `.github/scripts/bridge_generate.py`
   Asi, cualquier push de un pedido dispara la generacion.

> El archivo `bridge.json` (junto a la skill) define `repo_url` y `branch`.
> Apunta a la rama donde vive el workflow (idealmente `main`).

## Alcance de la skill

### En este proyecto (ya listo)
Vive en `.claude/skills/google-image/`; Claude la detecta automaticamente aqui.

### Global (todas tus conversaciones de Claude Code)
```bash
mkdir -p ~/.claude/skills
cp -r .claude/skills/google-image ~/.claude/skills/
```

### En Claude Cowork
Cowork lee `~/.claude/skills/`. Con el paso anterior queda disponible.
Reinicia Cowork si estaba abierto.

## Lo unico que necesitas en la maquina
- `git` con permiso de **push** al repo del puente (tu login normal de GitHub).
- **Nada** de API keys locales.

La primera vez, la skill clona el repo del puente en `~/.cache/imagen-bridge/`
(solo archivos del repo, ningun secreto) y lo reutiliza despues.

## Probar
```bash
python ~/.claude/skills/google-image/request_image.py "un cachorro feliz, foto realista" --out prueba.png
```
Veras `Esperando a que GitHub genere la imagen...` y al terminar
`OK: 1 imagen(es) generada(s) via GitHub` con el archivo `prueba.png`.

## Variables de entorno opcionales
- `IMAGEN_BRIDGE_BRANCH` — usar otra rama distinta a la de `bridge.json`.
- `IMAGEN_BRIDGE_REPO` — usar otra URL de repo.
- `IMAGEN_BRIDGE_DIR` — carpeta del checkout cache (default `~/.cache/imagen-bridge/repo`).
