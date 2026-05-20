"""
scraper.py
----------
Toda la lógica de scraping separada de la UI.
Intenta primero con requests. Si el sitio bloquea o devuelve
contenido vacío, cae automáticamente a Playwright.
"""

import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_URL = "https://ccleventos.pe"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": BASE_URL,
}

CATEGORIAS = {
    "🗂️ Todos":             "/listado-todos-los-eventos",
    "📚 Capacitaciones":    "/capacitaciones",
    "🎪 Ferias y Eventos":  "/ferias-y-eventos",
    "🛠️ Servicios":         "/servicios",
}

# Selectores CSS del sitio (ajustar si el sitio cambia su estructura)
CARD_SELECTORS = [
    "a[href*='/evento/']",
    ".card-evento",
    ".event-card",
    "[class*='evento-item']",
    "[class*='event-item']",
    "article",
]


def _parsear_cards(soup: BeautifulSoup) -> list[dict]:
    """Extrae eventos de un objeto BeautifulSoup."""
    eventos = []

    cards = []
    for sel in CARD_SELECTORS:
        cards = soup.select(sel)
        if cards:
            break

    for card in cards:
        # URL
        a_tag = card if card.name == "a" else card.find("a")
        url = a_tag.get("href", "") if a_tag else ""
        if url and not url.startswith("http"):
            url = BASE_URL + url

        # Título
        titulo_tag = card.select_one("h2, h3, h4, .titulo, .title, [class*='titulo'], [class*='title']")
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else card.get_text(" ", strip=True).split("\n")[0]

        # Fecha
        fecha_tag = card.select_one(".fecha, .date, [class*='fecha'], [class*='date'], time")
        fecha = fecha_tag.get_text(strip=True) if fecha_tag else ""

        # Categoría
        cat_tag = card.select_one(".categoria, .category, [class*='categoria'], [class*='tag']")
        categoria = cat_tag.get_text(strip=True) if cat_tag else ""

        # Precio
        precio_tag = card.select_one(".precio, .price, [class*='precio'], [class*='price']")
        precio = precio_tag.get_text(strip=True) if precio_tag else ""

        # Imagen
        img_tag = card.find("img")
        imagen = img_tag.get("src", "") or img_tag.get("data-src", "") if img_tag else ""
        if imagen and not imagen.startswith("http"):
            imagen = BASE_URL + imagen

        if titulo and len(titulo) > 3:
            eventos.append({
                "titulo":    titulo,
                "fecha":     fecha,
                "categoria": categoria,
                "precio":    precio,
                "url":       url,
                "imagen":    imagen,
            })

    return eventos


def scrape_con_requests(ruta: str) -> tuple[list[dict], str]:
    """
    Retorna (lista_eventos, método_usado).
    Si requests falla o devuelve vacío → usa Playwright automáticamente.
    """
    url = BASE_URL + ruta
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        eventos = _parsear_cards(soup)

        if eventos:
            return eventos, "requests"

        # El HTML llegó pero sin eventos → probablemente JS dinámico
        return scrape_con_playwright(ruta), "playwright (fallback automático)"

    except requests.RequestException as e:
        print(f"requests falló ({e}), usando Playwright...")
        return scrape_con_playwright(ruta), "playwright (fallback por error)"


def scrape_con_playwright(ruta: str) -> list[dict]:
    """Abre Chromium real para ejecutar el JavaScript del sitio."""
    url = BASE_URL + ruta
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=HEADERS["User-Agent"],
            extra_http_headers={"Accept-Language": "es-PE,es;q=0.9"},
        )
        page.goto(url, wait_until="networkidle", timeout=25000)

        # Scroll progresivo para contenido lazy-loaded
        for _ in range(6):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1.2)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "lxml")
    return _parsear_cards(soup)
