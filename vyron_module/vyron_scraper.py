import asyncio
import httpx
from bs4 import BeautifulSoup
import sqlite3
import logging
import csv

# Logging configuration
logging.basicConfig(
    filename='daemon.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

URL = "https://vyronsocial.com/"
DB_FILE = "vyron_social.db"
CSV_FILE = "vyron_social_export.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vyron_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT,
            content TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

async def fetch_and_parse():
    init_db()
    print("[🚀] Connecting to vyronsocial.com...")
    
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=15.0) as client:
        try:
            response = await client.get(URL)
            if response.status_code != 200:
                print(f"[❌] Failed with Status Code: {response.status_code}")
                logging.error(f"Vyron Social returned status {response.status_code}")
                return

            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extracting key elements (Headings, Text blocks, Links)
            scraped_items = []
            
            for elem in soup.find_all(['h1', 'h2', 'h3', 'p', 'a']):
                text = elem.get_text(strip=True)
                if text:
                    scraped_items.append((elem.name, text))

            # Store in SQLite
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.executemany("INSERT INTO vyron_data (section, content) VALUES (?, ?)", scraped_items)
            conn.commit()
            conn.close()

            # Export to CSV
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Section", "Content", "Scraped_At"])
                writer.writerows([(idx+1, tag, text, "NOW") for idx, (tag, text) in enumerate(scraped_items)])

            print(f"[✅] Extraction Complete! {len(scraped_items)} items saved to {DB_FILE} & {CSV_FILE}.")
            logging.info(f"Successfully scraped {len(scraped_items)} records from Vyron Social.")

        except Exception as e:
            print(f"[❌] Exception occurred: {e}")
            logging.error(f"Vyron Social Scraper Error: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_and_parse())
