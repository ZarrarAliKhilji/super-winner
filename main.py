import asyncio
import json
import os
import httpx
from core.client import fetch_page
from core.parser import parse_onion_results

QUERIES = ["financial", "security", "market", "intelligence"]
MAX_CONCURRENT_REQUESTS = 3

async def process_query(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, query: str):
    url = f"https://ahmia.fi/search/?q={query}"
    async with semaphore:
        print(f"[*] Executing concurrent request for query: '{query}'")
        html = await fetch_page(client, url)
        if html:
            data = parse_onion_results(html)
            print(f"[+] Found {len(data)} items for query: '{query}'")
            return data
        return []

async def main():
    os.makedirs("output", exist_ok=True)
    
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [process_query(client, semaphore, q) for q in QUERIES]
        results_nested = await asyncio.gather(*tasks)
        
        all_results = [item for sublist in results_nested for item in sublist]
        final_dataset = list({v['URL']: v for v in all_results}.values())
        
        print(f"\n[✨] Pipeline Finished! Total Unique Records: {len(final_dataset)}")
        
        output_path = "output/data.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_dataset, f, indent=4)
            
        print(f"📁 Enterprise JSON feed successfully compiled at '{output_path}'")

if __name__ == "__main__":
    asyncio.run(main())
