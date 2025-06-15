import logging
from playwright.sync_api import sync_playwright, Error as PlaywrightError
from .base_scraper import BaseScraper

class NilsDsaBlogScraper(BaseScraper):
    """
    Scraper for Nil's DS&A Blog.
    This scraper uses Playwright to handle the client-side rendered content.
    """
    name = "Nil's DS&A Blog"

    def __init__(self, url):
        super().__init__(url)

    def scrape(self):
        """
        Scrape the Nil's DS&A Blog content using Playwright.
        """
        items = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(self.url, wait_until='domcontentloaded', timeout=60000)

                page.wait_for_selector('article.card-border', timeout=90000)

                posts = page.locator('article.card-border').all()

                for post in posts:
                    title_element = post.locator('h2')
                    title = title_element.inner_text()
                    
                    link_element = post.locator('a:has(h2)')
                    href = link_element.get_attribute('href')
                    
                    if not href:
                        logging.warning(f"Warning: Could not find href for post with title '{title}'")
                        continue
                    source_url = "https://nilmamano.com" + href
                    
                    content_element = post.locator('p.text-muted-foreground')
                    content = content_element.first.inner_text() if content_element.count() > 0 else ""
                    author = "Nil Mamano"

                    items.append({
                        "title": title,
                        "content": content,
                        "content_type": "blog",
                        "source_url": source_url,
                        "author": author,
                        "user_id": ""
                    })

                browser.close()
        except PlaywrightError as e:
            logging.error(f"An error occurred during Playwright scraping: {e}")
            logging.error("Please ensure you have run 'playwright install' to download the necessary browser binaries.")
            return []
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return []

        return items 