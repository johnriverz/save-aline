import logging
from playwright.sync_api import sync_playwright, Error
from urllib.parse import urljoin
from .base_scraper import BaseScraper

class QuillBlogScraper(BaseScraper):
    """
    Scraper for the Quill.co blog.
    It uses Playwright to handle the client-side rendered content from Next.js.
    """
    name = "Quill.co Blog"

    def __init__(self, url, selectors=None):
        super().__init__(url)
        self.selectors = selectors

    def scrape(self):
        """
        Scrapes all blog posts from the Quill.co blog.
        """
        logging.info(f"Scraping Quill.co blog from {self.url}")
        items = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(self.url, wait_until='networkidle', timeout=60000)
                
                # Based on the visual structure, posts seem to be in `<a>` tags
                # that have a `<h4>` inside them.
                post_links = page.locator("a:has(h4)").all()
                
                urls_to_scrape = []
                for link in post_links:
                    href = link.get_attribute('href')
                    if href:
                        full_url = urljoin(self.url, href)
                        urls_to_scrape.append(full_url)
                
                logging.info(f"Found {len(urls_to_scrape)} blog post links to scrape.")

                for post_url in urls_to_scrape:
                    try:
                        logging.info(f"Scraping post: {post_url}")
                        post_page = browser.new_page()
                        post_page.goto(post_url, wait_until='networkidle', timeout=60000)

                        # Assuming the main title is the h1
                        title = post_page.locator('h1').first.inner_text()
                        
                        # Assuming the content is within a specific container.
                        # This selector is a guess and may need refinement.
                        content_container = post_page.locator('div.prose').first
                        content = content_container.inner_html()

                        items.append({
                            "title": title.strip(),
                            "content": content.strip(),
                            "content_type": "blog",
                            "source_url": post_url,
                            "author": "Quill.co", # Assuming author
                            "user_id": ""
                        })
                        post_page.close()
                    except Error as e:
                        logging.error(f"Could not scrape post at {post_url}: {e}")
                        if 'post_page' in locals() and not post_page.is_closed():
                            post_page.close()
                        continue

            except Error as e:
                logging.error(f"Could not load the main blog page {self.url}: {e}")
            finally:
                browser.close()

        logging.info(f"Successfully scraped {len(items)} items from {self.name}.")
        return items 