
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


class YouTubeAgent:
    def __init__(self, channel_url, max_videos=5):
        self.channel_url = channel_url
        self.max_videos = max_videos

    def scrape(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        try:
            driver.get(self.channel_url + "/videos")
            time.sleep(5)

            videos = []
            elements = driver.find_elements(By.XPATH, '//a[@id="video-title"]')

            print(f"🔍 Found {len(elements)} video titles on channel")

            for i, element in enumerate(elements[:self.max_videos]):
                try:
                    title = element.get_attribute("title")
                    href = element.get_attribute("href")
                    driver.execute_script("window.open(arguments[0]);", href)
                    driver.switch_to.window(driver.window_handles[1])
                    time.sleep(3)
                    desc_elem = driver.find_elements(By.XPATH, '//yt-formatted-string[@class="content style-scope ytd-video-secondary-info-renderer"]')
                    description = desc_elem[0].text if desc_elem else "No description found."
                    comment_elems = driver.find_elements(By.XPATH, '//ytd-comment-thread-renderer//ytd-expander//yt-formatted-string')
                    comments = [c.text for c in comment_elems[:5]]

                    videos.append({
                        "title": title,
                        "url": href,
                        "description": description,
                        "comments": comments
                    })

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception as e:
                    print(f"⚠️ Error parsing video {i}: {e}")

            print(f"✅ Scraped {len(videos)} videos from channel")
            return videos

        finally:
            driver.quit()


def find_youtube_channel_from_website(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if "youtube.com/channel/" in href or "youtube.com/c/" in href or "youtube.com/@":
                match = re.search(r"(https?://)?(www\.)?youtube\.com[^\"\s]+", href)
                if match:
                    return match.group(0)
        return None
    except Exception as e:
        print(f"❌ Error while fetching or parsing website: {e}")
        return None


if __name__ == "__main__":
    website_url = input("🌐 Enter a website URL to search for their YouTube channel: ").strip()
    yt_channel_url = find_youtube_channel_from_website(website_url)

    if yt_channel_url:
        print(f"📺 Found YouTube channel: {yt_channel_url}")
    else:
        print("❌ No YouTube channel found on the website.")
        fallback = input("🔁 Want to manually enter the YouTube channel URL? (yes/no): ").strip().lower()
        if fallback == "yes":
            yt_channel_url = input("✏️ Enter the YouTube channel URL: ").strip()

    if yt_channel_url:
        agent = YouTubeAgent(yt_channel_url, max_videos=5)
        videos = agent.scrape()

        for i, video in enumerate(videos):
            print(f"\n🎬 Video {i+1}: {video['title']}")
            print(f"🔗 {video['url']}")
            print(f"📝 Description: {video['description'][:200]}...")
            print("💬 Comments:")
            for c in video['comments']:
                print(f" - {c}")
            print("-" * 40)
