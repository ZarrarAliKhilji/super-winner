from bs4 import BeautifulSoup

def parse_onion_results(html_content: str) -> list[dict]:
    """Parses HTML and extracts unique onion links and titles safely."""
    soup = BeautifulSoup(html_content, "html.parser")
    results = []
    
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".onion" in href:
            title = a.text.strip() or "N/A"
            results.append({"Title": title, "URL": href})
            
    unique_results = list({v['URL']: v for v in results}.values())
    return unique_results
