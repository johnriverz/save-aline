import requests
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
import logging
from urllib.parse import urljoin

class InterviewingIoInterviewGuidesScraper(BaseScraper):
    """
    Scrapes the interview guides from Interviewing.io.
    """
    name = "Interviewing.io Interview Guides"

    def __init__(self, url, selectors):
        super().__init__(url)
        self.selectors = selectors

    def scrape(self):
        """
        Scrape the Interviewing.io Interview Guides from the main 'learn' page.
        """
        items = []
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the "Interview Guides" section
            section_header_id = self.selectors.get("section_header_id")
            guides_header = soup.find('h2', id=section_header_id)
            if not guides_header:
                logging.warning("Could not find the 'Interview Guides' section.")
                return []

            # The guides are in a div that is a sibling of the h2
            guides_container_selector = self.selectors.get("guides_container_selector")
            guides_container = guides_header.find_next_sibling(guides_container_selector)
            if not guides_container:
                logging.warning("Could not find the guides section container.")
                return []

            # Find all guide links within that section
            guide_link_selector = self.selectors.get("guide_link_selector")
            for guide_link in guides_container.find_all(guide_link_selector, href=True):
                # The structure is a bit nested, so we need to find the relevant text
                title_selector = self.selectors.get("title_selector")
                title_element = guide_link.find(title_selector)
                title = title_element.get_text(strip=True) if title_element else 'No Title'

                content_selector = self.selectors.get("content_selector")
                content_element = guide_link.find(content_selector)
                content = content_element.get_text(strip=True) if content_element else ''
                
                source_url = guide_link['href']
                if not source_url.startswith('http'):
                    # Ensure it's a full URL
                    source_url = f"https://interviewing.io{source_url}" if source_url.startswith('/') else source_url

                items.append({
                    "title": title,
                    "content": content,
                    "content_type": "other", # These are guides, not blog posts
                    "source_url": source_url,
                    "author": "interviewing.io",
                    "user_id": ""
                })

            return items

        except requests.exceptions.RequestException as e:
            logging.error(f"Error scraping interview guides: {e}")
            return [] 