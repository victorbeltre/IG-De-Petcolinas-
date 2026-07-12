# Instalar la skill `google-image` para usarla en cualquier lugar

Esta skill funciona en 3 alcances. Elige segun donde la quieras usar.

## 1. Solo en este proyecto (ya esta lista)
Al vivir en `.claude/skills/google-image/` dentro del repo, Claude Code la
detecta automaticamente cuando trabajas en esta carpeta. No hay que hacer nada.

## 2. En TODAS tus conversaciones de Claude Code (global, tu maquina)
Copia la carpeta a tu directorio de skills del usuario:

```bash
mkdir -p ~/.claude/skills
cp -r .claude/skills/google-image ~/.claude/skills/
```

Desde ahi estara disponible en cualquier proyecto/carpeta.

## 3. En Claude Cowork (app de escritorio)
Cowork lee las skills del mismo directorio del usuario: `~/.claude/skills/`.
Con el paso 2 ya queda disponible en Cowork. Reinicia Cowork si estaba abierto.

---

## Configurar la API key (una sola vez)
La skill necesita tu key de Google AI Studio. Guardala UNA vez de forma
persistente (no la pongas en el repo):

**Opcion A — archivo local (recomendado para Cowork):**
```bash
printf 'TU_API_KEY_AQUI' > ~/.google_ai_key
chmod 600 ~/.google_ai_key
```

**Opcion B — variable de entorno (agregala a tu ~/.zshrc o ~/.bashrc):**
```bash
export GOOGLE_AI_KEY='TU_API_KEY_AQUI'
```

> La key nunca se imprime ni se guarda en el repositorio. Si algun dia la
> rotas, solo actualiza el archivo o la variable.

## Probar que funciona
```bash
python ~/.claude/skills/google-image/generate_image.py "un cachorro feliz, foto realista" --out prueba.png
```
Si ves `OK: 1 imagen(es) generada(s)` y el archivo `prueba.png`, quedo lista.
