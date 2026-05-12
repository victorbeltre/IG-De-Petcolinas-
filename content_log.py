"""
Historial de posts publicados por PetColinas.
Lee y escribe content_log.json para evitar repeticion y guiar la rotacion
de contenido segun los pilares del plan de campana.
"""

import json
import datetime
from pathlib import Path
from typing import Optional

LOG_FILE = Path("content_log.json")
LOOKBACK_DAYS = 7


def _load() -> list:
    if not LOG_FILE.exists():
        return []
    try:
        return json.loads(LOG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(entries: list) -> None:
    LOG_FILE.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def append_post(tipo: str, tema: str, raza: str, mes_campana: str,
                date: Optional[datetime.date] = None) -> None:
    """Registra un post publicado en el historial."""
    if date is None:
        date = datetime.date.today()
    entries = _load()
    entries.append({
        "fecha": date.isoformat(),
        "tipo": tipo,
        "tema": tema,
        "raza": raza,
        "mes_campana": mes_campana,
    })
    # Mantener solo los ultimos 90 dias para no crecer indefinidamente
    cutoff = (datetime.date.today() - datetime.timedelta(days=90)).isoformat()
    entries = [e for e in entries if e["fecha"] >= cutoff]
    _save(entries)


def get_recent_posts(days: int = LOOKBACK_DAYS) -> list:
    """Retorna los posts de los ultimos N dias."""
    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    return [e for e in _load() if e["fecha"] >= cutoff]


def get_type_frequency(days: int = LOOKBACK_DAYS) -> dict:
    """Retorna cuantas veces se publico cada tipo en los ultimos N dias."""
    freq: dict = {}
    for post in get_recent_posts(days):
        freq[post["tipo"]] = freq.get(post["tipo"], 0) + 1
    return freq


def get_recent_breeds(days: int = LOOKBACK_DAYS) -> list:
    """Retorna las razas usadas recientemente para evitar repeticion."""
    return [p["raza"] for p in get_recent_posts(days)]


def suggest_content_type(servicio_estrella: str, days: int = LOOKBACK_DAYS) -> str:
    """
    Sugiere el tipo de contenido mas necesario segun los pilares del plan
    y lo que ya se publico recientemente.

    Pilares semanales (7 posts):
      grooming    -> 3 posts
      comunidad   -> 2 posts
      veterinaria -> 1 post
      membresia   -> 1 post
    """
    targets = {"grooming": 3, "comunidad": 2, "veterinaria": 1, "membresia": 1}
    freq = get_type_frequency(days)

    # Calcular deficit de cada pilar (target - publicados)
    deficit = {t: targets[t] - freq.get(t, 0) for t in targets}

    # El servicio estrella del mes tiene prioridad si tiene deficit
    if deficit.get(servicio_estrella, 0) > 0:
        return servicio_estrella

    # Si no, el tipo con mayor deficit
    return max(deficit, key=lambda t: deficit[t])


def format_history_for_prompt(days: int = LOOKBACK_DAYS) -> str:
    """
    Formatea el historial reciente como texto para incluir en el prompt de Claude.
    """
    recent = get_recent_posts(days)
    freq = get_type_frequency(days)

    if not recent:
        return "=== HISTORIAL: No hay posts previos registrados. ==="

    lines = [f"=== HISTORIAL DE POSTS (ultimos {days} dias) ==="]
    for p in sorted(recent, key=lambda x: x["fecha"], reverse=True)[:5]:
        lines.append(f"  {p['fecha']} | {p['tipo']:12} | {p['raza']:20} | {p['tema'][:50]}")

    lines.append("")
    lines.append("Frecuencia reciente por tipo:")
    targets = {"grooming": 3, "comunidad": 2, "veterinaria": 1, "membresia": 1}
    for tipo, target in targets.items():
        count = freq.get(tipo, 0)
        estado = "OK" if count >= target else f"FALTAN {target - count}"
        lines.append(f"  {tipo:12} -> {count}/{target} posts  [{estado}]")

    razas_recientes = get_recent_breeds(days)
    if razas_recientes:
        lines.append("")
        lines.append(f"Razas usadas recientemente (EVITAR repetir): {', '.join(razas_recientes[-5:])}")

    lines.append("=== FIN HISTORIAL ===")
    return "\n".join(lines)
