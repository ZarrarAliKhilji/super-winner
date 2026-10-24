import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

async def fetch_page(client: httpx.AsyncClient, url: str) -> str | None:
    """Safely fetches a URL using an active async client with error handling."""
    try:
        response = await client.get(url, headers=HEADERS, timeout=15.0)
        if response.status_code == 200:
            return response.text
        print(f"[-] Non-200 status code received ({response.status_code}) for: {url}")
        return None
    except httpx.RequestError as e:
        print(f"[!] Network error occurred for {url}: {e}")
        return None
