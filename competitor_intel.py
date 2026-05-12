"""
Inteligencia competitiva para PetColinas.
Analiza veterinarias y peluquerias caninas en Santo Domingo / RD
para identificar patrones de contenido y oportunidades de diferenciacion.

Modos de uso:
  1. Busqueda automatica via DuckDuckGo (datos publicos indexados)
  2. Analisis manual: pasar archivo JSON con datos copiados de Instagram

Uso:
  python competitor_intel.py                        # busqueda automatica
  python competitor_intel.py --input datos.json     # analisis de datos manuales
  python competitor_intel.py --handles @vet1 @vet2  # handles especificos

Genera:
  competitor_report.json  -> datos brutos recolectados
  competitor_insights.md  -> reporte de estrategia listo para leer
"""

import os
import re
import json
import time
import argparse
import datetime
from pathlib import Path

import anthropic
import requests

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# ---------------------------------------------------------------------------
# Competidores conocidos en RD (veterinarias y peluquerias caninas)
# Actualizar con nuevos competidores segun se identifiquen
# ---------------------------------------------------------------------------

COMPETITORS = [
    {"handle": "@veterinariamascotas_rd",  "nombre": "Veterinaria Mascotas RD",  "zona": "Santo Domingo"},
    {"handle": "@groomingrd",              "nombre": "Grooming RD",              "zona": "Santo Domingo"},
    {"handle": "@petshoprd",               "nombre": "Pet Shop RD",              "zona": "Nacional"},
    {"handle": "@peluqueriacaninard",      "nombre": "Peluqueria Canina RD",     "zona": "Santo Domingo"},
    {"handle": "@clinicaveterinariasd",    "nombre": "Clinica Veterinaria SD",   "zona": "Santo Domingo Este"},
    {"handle": "@petloversrd",             "nombre": "Pet Lovers RD",            "zona": "Santiago"},
    {"handle": "@groomingpremiumrd",       "nombre": "Grooming Premium RD",      "zona": "Santo Domingo"},
    {"handle": "@vetclinicacanina",        "nombre": "Vet Clinica Canina",       "zona": "Santo Domingo Norte"},
]

PETCOLINAS_PROFILE = """
PetColinas (@petcolinas):
- Veterinaria + Peluqueria Canina en Plaza Las Colinas, SDO
- WhatsApp: 809-752-6806
- Servicios: grooming (bano desde RD$699), veterinaria (consulta RD$1,500), membresias (desde RD$2,800/mes)
- Horario: todos los dias EXCEPTO martes
- Estilo: calido, dominicano, cercano
- Colores: verde oscuro + naranja + dorado
- Diferenciadores actuales: membresias con turno VIP, formula Portrait para imagenes editoriales
"""

ANALYSIS_PROMPT = """
Eres un estratega de marketing digital especializado en negocios locales dominicanos
y en Instagram como canal de ventas. Tu tarea es analizar a la competencia de PetColinas
y extraer estrategias accionables.

PERFIL DE PETCOLINAS (nuestro cliente):
{petcolinas}

DATOS DE COMPETIDORES RECOLECTADOS:
{competitor_data}

Analiza estos datos y produce un reporte estructurado en formato JSON con este esquema exacto:

{{
  "fecha_analisis": "<fecha ISO>",
  "resumen_ejecutivo": "<3-4 oraciones sobre el panorama competitivo en RD>",
  "patrones_detectados": {{
    "tipos_contenido_mas_usados": ["<tipo1>", "<tipo2>", "..."],
    "tono_predominante": "<descripcion del tono general de la competencia>",
    "hashtags_populares": ["<hashtag1>", "<hashtag2>", "..."],
    "frecuencia_posting": "<estimado de posts por semana de la competencia>",
    "horarios_pico": "<cuando publican mas>",
    "formatos_visuales": "<descripcion de estilos de imagen predominantes>"
  }},
  "fortalezas_competencia": [
    {{"fortaleza": "<que hacen bien>", "ejemplo": "<ejemplo concreto>"}}
  ],
  "debilidades_competencia": [
    {{"debilidad": "<donde fallan>", "oportunidad_petcolinas": "<como PetColinas puede diferenciarse>"}}
  ],
  "oportunidades_diferenciacion": [
    {{
      "oportunidad": "<gap detectado>",
      "estrategia": "<como PetColinas puede explotarla>",
      "tipo_contenido": "<formato recomendado>",
      "prioridad": "alta|media|baja"
    }}
  ],
  "recomendaciones_contenido": [
    {{
      "tema": "<tema de post recomendado>",
      "por_que": "<por que esto diferencia a PetColinas>",
      "caption_idea": "<idea de caption en tono dominicano>",
      "tipo": "<grooming|veterinaria|membresia|educativo|comunidad>"
    }}
  ],
  "hashtags_recomendados": {{
    "adoptar": ["<hashtag que usa la competencia y PetColinas deberia usar>"],
    "evitar": ["<hashtag saturado o inefectivo>"],
    "propios_unicos": ["<hashtag que PetColinas puede reclamar como propio>"]
  }},
  "score_competencia": {{
    "contenido_visual": "<1-10 con justificacion breve>",
    "engagement_estimado": "<1-10>",
    "consistencia": "<1-10>",
    "diferenciacion_petcolinas": "<1-10 — que tan diferente es PetColinas ya>"
  }}
}}

Sé especifico, critico y accionable. Prioriza insights que PetColinas pueda implementar
esta semana en su calendario editorial.
"""

# ---------------------------------------------------------------------------
# Busqueda web via DuckDuckGo (HTML scraping de resultados publicos)
# No requiere API key. Respeta robots.txt de IG al no acceder a IG directamente.
# ---------------------------------------------------------------------------

DDG_URL = "https://html.duckduckgo.com/html/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PetColinasResearch/1.0)",
}


def _ddg_search(query: str, max_results: int = 5) -> list[dict]:
    """Busca en DuckDuckGo y retorna snippets de resultados."""
    try:
        resp = requests.post(
            DDG_URL,
            data={"q": query, "kl": "us-es"},
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code != 200:
            return []

        # Extraer snippets del HTML
        snippets = re.findall(
            r'class="result__snippet"[^>]*>(.*?)</a>',
            resp.text,
            re.DOTALL,
        )
        titles = re.findall(
            r'class="result__a"[^>]*>(.*?)</a>',
            resp.text,
            re.DOTALL,
        )

        results = []
        for title, snippet in zip(titles[:max_results], snippets[:max_results]):
            clean_title = re.sub(r"<[^>]+>", "", title).strip()
            clean_snippet = re.sub(r"<[^>]+>", "", snippet).strip()
            if clean_snippet:
                results.append({"titulo": clean_title, "snippet": clean_snippet})

        return results
    except Exception as e:
        print(f"    Aviso: busqueda fallida ({e})")
        return []


def search_competitor(competitor: dict) -> dict:
    """Recopila datos publicos de un competidor via busqueda web."""
    handle = competitor["handle"]
    nombre = competitor["nombre"]
    print(f"  Buscando: {handle} ({nombre})...")

    queries = [
        f'site:instagram.com {handle} veterinaria grooming "Santo Domingo"',
        f'"{nombre}" instagram mascotas Dominican Republic posts',
        f'{handle} instagram grooming canino "republica dominicana"',
    ]

    all_snippets = []
    for q in queries:
        results = _ddg_search(q, max_results=3)
        all_snippets.extend(results)
        time.sleep(1)  # respetar rate limits

    return {
        "handle": handle,
        "nombre": nombre,
        "zona": competitor.get("zona", "RD"),
        "snippets_encontrados": len(all_snippets),
        "datos_web": all_snippets,
    }


# ---------------------------------------------------------------------------
# Analisis con Claude
# ---------------------------------------------------------------------------

def analyze_with_claude(competitor_data: list[dict]) -> dict:
    """Envia los datos recolectados a Claude para analisis estrategico."""
    print("\n[Claude] Analizando datos competitivos...")

    competitor_text = json.dumps(competitor_data, ensure_ascii=False, indent=2)
    prompt = ANALYSIS_PROMPT.format(
        petcolinas=PETCOLINAS_PROFILE,
        competitor_data=competitor_text[:8000],  # limitar tokens
    )

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=(
            "Eres un estratega de marketing digital experto en negocios locales "
            "dominicanos e Instagram como canal de adquisicion de clientes. "
            "Produces analisis criticos, especificos y accionables."
        ),
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"Claude no retorno JSON valido:\n{raw[:500]}")

    return json.loads(match.group())


# ---------------------------------------------------------------------------
# Generacion de reporte Markdown legible
# ---------------------------------------------------------------------------

def generate_markdown_report(insights: dict, output_path: str = "competitor_insights.md") -> None:
    """Convierte el analisis JSON a un reporte Markdown legible."""
    today = datetime.date.today().strftime("%d de %B de %Y")
    lines = [
        f"# Reporte de Inteligencia Competitiva — PetColinas",
        f"**Fecha:** {today}",
        "",
        "---",
        "",
        "## Resumen Ejecutivo",
        "",
        insights.get("resumen_ejecutivo", ""),
        "",
        "---",
        "",
        "## Patrones Detectados en la Competencia",
        "",
    ]

    patrones = insights.get("patrones_detectados", {})
    if patrones:
        lines += [
            f"- **Tipos de contenido mas usados:** {', '.join(patrones.get('tipos_contenido_mas_usados', []))}",
            f"- **Tono predominante:** {patrones.get('tono_predominante', '')}",
            f"- **Frecuencia de posting:** {patrones.get('frecuencia_posting', '')}",
            f"- **Formatos visuales:** {patrones.get('formatos_visuales', '')}",
            f"- **Hashtags populares:** {' '.join(patrones.get('hashtags_populares', []))}",
            "",
        ]

    lines += ["---", "", "## Oportunidades de Diferenciacion", ""]
    for opp in insights.get("oportunidades_diferenciacion", []):
        prioridad = opp.get("prioridad", "media").upper()
        lines += [
            f"### [{prioridad}] {opp.get('oportunidad', '')}",
            f"**Estrategia:** {opp.get('estrategia', '')}",
            f"**Formato recomendado:** {opp.get('tipo_contenido', '')}",
            "",
        ]

    lines += ["---", "", "## Ideas de Contenido para Esta Semana", ""]
    for i, rec in enumerate(insights.get("recomendaciones_contenido", []), 1):
        lines += [
            f"### {i}. {rec.get('tema', '')} `[{rec.get('tipo', '')}]`",
            f"**Por que diferencia:** {rec.get('por_que', '')}",
            f"**Idea de caption:** _{rec.get('caption_idea', '')}_",
            "",
        ]

    lines += ["---", "", "## Estrategia de Hashtags", ""]
    hashtags = insights.get("hashtags_recomendados", {})
    if hashtags:
        lines += [
            f"**Adoptar:** {' '.join(hashtags.get('adoptar', []))}",
            f"**Evitar:** {' '.join(hashtags.get('evitar', []))}",
            f"**Propios unicos:** {' '.join(hashtags.get('propios_unicos', []))}",
            "",
        ]

    lines += ["---", "", "## Score de Competencia vs PetColinas", ""]
    scores = insights.get("score_competencia", {})
    if scores:
        for key, val in scores.items():
            label = key.replace("_", " ").title()
            lines.append(f"- **{label}:** {val}")
        lines.append("")

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"  Reporte guardado: {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Analisis competitivo para PetColinas")
    parser.add_argument("--input", help="JSON con datos de competidores ya recolectados")
    parser.add_argument("--handles", nargs="+", help="Handles de Instagram a analizar (@handle)")
    parser.add_argument("--skip-search", action="store_true",
                        help="Omitir busqueda web y solo analizar con datos previos")
    args = parser.parse_args()

    today = datetime.date.today()
    print(f"\n{'='*55}")
    print(f"  INTEL COMPETITIVA PETCOLINAS — {today.strftime('%d/%m/%Y')}")
    print(f"{'='*55}\n")

    # Determinar lista de competidores
    if args.handles:
        competitors = [{"handle": h, "nombre": h, "zona": "RD"} for h in args.handles]
    else:
        competitors = COMPETITORS

    # Cargar o recolectar datos
    if args.input:
        print(f"[1/3] Cargando datos desde {args.input}...")
        with open(args.input, encoding="utf-8") as f:
            competitor_data = json.load(f)
    elif args.skip_search and Path("competitor_report.json").exists():
        print("[1/3] Usando datos previos (competitor_report.json)...")
        with open("competitor_report.json", encoding="utf-8") as f:
            competitor_data = json.load(f)
    else:
        print(f"[1/3] Buscando datos publicos de {len(competitors)} competidores...")
        competitor_data = []
        for comp in competitors:
            data = search_competitor(comp)
            competitor_data.append(data)
            print(f"    {data['handle']}: {data['snippets_encontrados']} snippets")

        with open("competitor_report.json", "w", encoding="utf-8") as f:
            json.dump(competitor_data, f, ensure_ascii=False, indent=2)
        print(f"  Datos brutos guardados: competitor_report.json")

    # Analisis con Claude
    print("\n[2/3] Analizando con Claude...")
    insights = analyze_with_claude(competitor_data)

    with open("competitor_insights.json", "w", encoding="utf-8") as f:
        json.dump(insights, f, ensure_ascii=False, indent=2)

    # Generar reporte Markdown
    print("\n[3/3] Generando reporte...")
    generate_markdown_report(insights)

    # Mostrar resumen en consola
    print(f"\n{'='*55}")
    print("  RESUMEN DE OPORTUNIDADES")
    print(f"{'='*55}")
    for opp in insights.get("oportunidades_diferenciacion", [])[:3]:
        prio = opp.get("prioridad", "?").upper()
        print(f"  [{prio}] {opp.get('oportunidad', '')}")

    print(f"\n  Ideas de contenido generadas: {len(insights.get('recomendaciones_contenido', []))}")
    print(f"\n  Ver reporte completo: competitor_insights.md")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
