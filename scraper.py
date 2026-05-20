import requests

API_URL = "https://ccleventos.pe/backend/api/events"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def obtener_eventos():
    response = requests.get(API_URL, headers=HEADERS, timeout=15)

    response.raise_for_status()

    data = response.json()

    eventos = []

    # inspecciona cómo viene el JSON
    # probablemente data sea una lista

    for item in data:
        eventos.append({
            "titulo": item.get("title", ""),
            "fecha": item.get("date", ""),
            "categoria": item.get("category", ""),
            "precio": item.get("price", ""),
            "url": item.get("url", ""),
            "imagen": item.get("image", ""),
        })

    return eventos