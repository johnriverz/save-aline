import requests
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
import logging

class InterviewingIoCompanyGuidesScraper(BaseScraper):
    """
    Scraper for Interviewing.io Company Guides.
    """
    def __init__(self, url, selectors):
        super().__init__(url)
        self.selectors = selectors

    def scrape(self):
        """
        Scrape the Interviewing.io Company Guides.
        This involves a multi-step process:
        1. Scrape the main topics page to find all company guide URLs.
        2. Scrape each individual company guide page for its content.
        """
        
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            guide_urls = set() # Use a set to avoid duplicates
            # Find all links that seem to point to a company guide page
            url_pattern = self.selectors.get("guide_url_pattern")
            for a in soup.find_all('a', href=True):
                if url_pattern and url_pattern in a['href']:
                    full_url = a['href']
                    if not full_url.startswith('http'):
                        full_url = f"https://interviewing.io{a['href']}"
                    guide_urls.add(full_url)
            
            logging.info(f"Found {len(guide_urls)} company guide URLs.")

            all_items = []
            for url in guide_urls:
                items = self._scrape_guide_page(url)
                if items:
                    all_items.extend(items)

            return all_items

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching the main topics page: {e}")
            return []

    def _scrape_guide_page(self, url):
        """
        Scrape a single company guide page for its content.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            title_selector = self.selectors.get("title_selector")
            title_element = soup.find(title_selector)
            title = title_element.get_text(strip=True) if title_element else 'No Title'
            
            content_container_selector = self.selectors.get("content_container_selector")
            content_container = soup.select_one(content_container_selector)
            content = ""
            if content_container:
                content_element_selectors = self.selectors.get("content_element_selectors", [])
                # Find all text-based elements within the container
                for element in content_container.find_all(content_element_selectors):
                    content += element.get_text(strip=True) + "\\n\\n"
            else:
                content = "No Content Found"
                logging.warning(f"No content container found for {url}")

            return [{
                "title": title,
                "content": content,
                "content_type": "other",
                "source_url": url,
                "author": "interviewing.io",
                "user_id": ""
            }]

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching guide page {url}: {e}")
            return None 