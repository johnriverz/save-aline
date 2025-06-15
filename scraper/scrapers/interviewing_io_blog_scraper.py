import json
import requests
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
import logging

class InterviewingIoBlogScraper(BaseScraper):
    """
    Scraper for the Interviewing.io blog.
    It works by finding the '__NEXT_DATA__' script tag in the HTML
    and parsing the JSON content to extract blog post data.
    """
    def __init__(self, url, selectors):
        super().__init__(url)
        self.selectors = selectors

    def scrape(self):
        """
        Scrape the Interviewing.io blog content.
        """
        items = []
        try:
            response = requests.get(self.url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching page: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        next_data_script_id = self.selectors.get("next_data_script_id")
        next_data_script = soup.find('script', {'id': next_data_script_id})

        if not next_data_script:
            logging.error("Could not find __NEXT_DATA__ script tag.")
            return []
        
        try:
            next_data = json.loads(next_data_script.string)
            blogs = next_data.get('props', {}).get('pageProps', {}).get('blogs', [])
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            logging.error(f"Failed to parse __NEXT_DATA__ JSON: {e}")
            return []

        for post in blogs:
            attributes = post.get('attributes', {})
            if not attributes:
                continue

            authors_data = attributes.get('authors', {}).get('data', [])
            author = authors_data[0].get('attributes', {}).get('name') if authors_data else "Unknown"
            
            items.append({
                "title": attributes.get('title'),
                "content": attributes.get('excerpt'),
                "content_type": "blog",
                "source_url": f"https://interviewing.io/blog/{attributes.get('slug')}",
                "author": author,
                "user_id": ""
            })

        return items 