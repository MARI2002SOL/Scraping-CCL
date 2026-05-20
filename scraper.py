"""
scraper.py — CCL Eventos
Consume directamente la API JSON del backend.
"""
 
import requests
from datetime import datetime, timezone
 
API_URL = "https://ccleventos.pe/backend/api/events"
 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://ccleventos.pe/",
}
 
CATEGORIAS = ["Todas", "Capacitaciones", "Ferias y Eventos", "Servicios"]
 
 
def _formatear_fecha(iso: str) -> str:
    """Convierte '2026-06-08T13:30:00.000Z' → 'lun 08 jun 2026, 08:30'"""
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        dt_lima = dt.astimezone(timezone.utc)  # UTC-5, ajusta si quieres hora local
        return dt_lima.strftime("%d %b %Y, %H:%M UTC")
    except Exception:
        return iso
 
 
def obtener_eventos(categoria: str = "Todas") -> list[dict]:
    resp = requests.get(API_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
 
    eventos = []
    for ev in data:
        # Filtrar por categoría si no es "Todas"
        if categoria != "Todas" and ev.get("Categoria", "") != categoria:
            continue
 
        precio_socios     = ev.get("PrecioSocios", 0) or 0
        precio_no_socios  = ev.get("PrecioNoSocios", 0) or 0
 
        if precio_socios == 0 and precio_no_socios == 0:
            precio_txt = "Gratuito"
        else:
            precio_txt = f"S/ {precio_socios:,.0f} socios · S/ {precio_no_socios:,.0f} no socios"
 
        eventos.append({
            "titulo":     ev.get("Nombre", ""),
            "fecha":      _formatear_fecha(ev.get("FechaInicio", "")),
            "categoria":  ev.get("Categoria", ""),
            "tipo":       ev.get("TipoEvento", ""),
            "lugar":      ev.get("LugarEvento", ""),
            "precio":     precio_txt,
            "clase":      ev.get("ClaseEvento", ""),
            "imagen":     ev.get("BannerURL") or "",
            "url":        f"https://ccleventos.pe/evento/{ev.get('EventoId', '')}",
            "descripcion": ev.get("Descripcion") or "",
        })
 
    return eventos
 