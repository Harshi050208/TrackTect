import requests
from bs4 import BeautifulSoup
import json
import os


class ScraperAgent:
    def __init__(self, urls_file="data/urls.json"):
        self.urls = self.load_urls(urls_file)

    def load_urls(self, file_path):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_path, file_path)
        with open(full_path, 'r') as f:
            data = json.load(f)
        return data.get("competitors", [])


    def scrape_site(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            return text[:3000]  # limit output to avoid overload
        except Exception as e:
            print(f"[ERROR] Failed to scrape {url}: {e}")
            return None

    def run(self):
        scraped_data = {}
        for url in self.urls:
            print(f"[INFO] Scraping: {url}")
            content = self.scrape_site(url)
            if content:
                scraped_data[url] = content
        return scraped_data


if __name__ == "__main__":
    agent = ScraperAgent()
    result = agent.run()
    for url, content in result.items():
        print(f"\n[SCRAPED] {url}:\n{content[:500]}...\n")
