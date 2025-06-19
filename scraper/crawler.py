import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from .agent_scraper import KadoaInspiredScraper
import logging

logger = logging.getLogger(__name__)

class Crawler:
    """
    Crawls a website by finding its sitemap and scraping all the URLs found.
    """
    def __init__(self):
        self.scraper = KadoaInspiredScraper()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _find_sitemap_url(self, base_url: str) -> str | None:
        """Finds the sitemap URL from the robots.txt file."""
        robots_url = urljoin(base_url, "/robots.txt")
        try:
            response = self.session.get(robots_url, timeout=10)
            response.raise_for_status()
            for line in response.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    return line.split(":", 1)[1].strip()
        except requests.RequestException as e:
            logger.warning(f"Could not fetch or parse robots.txt at {robots_url}: {e}")
        return None

    def _get_urls_from_sitemap(self, sitemap_url: str) -> list[str]:
        """Parses a sitemap (including sitemap indexes) and returns a list of page URLs."""
        urls = []
        try:
            response = self.session.get(sitemap_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")

            if soup.find('sitemapindex'):
                # This is a sitemap index file, recursively parse the sitemaps it points to
                for loc in soup.select("sitemap > loc"):
                    urls.extend(self._get_urls_from_sitemap(loc.text))
            else:
                # This is a regular sitemap
                urls = [loc.text for loc in soup.select("url > loc")]
        except requests.RequestException as e:
            logger.warning(f"Could not fetch or parse sitemap {sitemap_url}: {e}")
        return urls

    def _get_links_from_page(self, html_content: str, base_url: str, path_prefix: str | None = None) -> list[str]:
        """Extracts internal links, optionally filtering by a path prefix."""
        soup = BeautifulSoup(html_content, "html.parser")
        links = set()
        base_domain = urlparse(base_url).netloc
        
        for a_tag in soup.find_all("a", href=True):
            href = a_tag['href']
            # Join relative URLs with the base URL
            full_url = urljoin(base_url, href)
            parsed_full_url = urlparse(full_url)
            
            # Check if the link is on the same domain
            if parsed_full_url.netloc == base_domain:
                # If a path_prefix is specified, check if the link's path starts with it
                if path_prefix:
                    if parsed_full_url.path.startswith(path_prefix):
                        links.add(full_url)
                else:
                    # If no prefix (i.e., we started from the root), add all internal links
                    links.add(full_url)
        return list(links)

    def crawl(self, base_url: str) -> dict:
        """
        Orchestrates the crawl: finds sitemap, gets URLs, and scrapes each one.
        If no sitemap is found, it falls back to scraping links found on the base URL.
        """
        logger.info(f"Starting crawl for {base_url}")
        all_urls = []
        
        sitemap_url = self._find_sitemap_url(base_url)
        if sitemap_url:
            logger.info(f"Found sitemap: {sitemap_url}")
            all_urls = self._get_urls_from_sitemap(sitemap_url)
            logger.info(f"Found {len(all_urls)} URLs in sitemap to scrape.")
        else:
            logger.warning(f"No sitemap found for {base_url}. Falling back to page link extraction.")
            # Fallback: scrape the base_url and get links from it
            try:
                response = self.session.get(base_url, timeout=10)
                response.raise_for_status()
                
                # --- Intelligent Path Scoping ---
                # Infer the scope from the initial URL to only crawl relevant links.
                parsed_base_url = urlparse(base_url)
                path_parts = parsed_base_url.path.strip('/').split('/')
                
                # If the path has segments (e.g., /blog/...), use the first segment as the scope.
                # Otherwise, we are at the root, so we don't apply a path prefix filter.
                allowed_prefix = f"/{path_parts[0]}/" if path_parts and path_parts[0] else None
                
                if allowed_prefix:
                    logger.info(f"Crawling is scoped to paths starting with: {allowed_prefix}")

                all_urls = self._get_links_from_page(response.text, base_url, path_prefix=allowed_prefix)
                # Also include the base_url itself in the list to be scraped
                if base_url not in all_urls:
                    all_urls.insert(0, base_url)
                logger.info(f"Found {len(all_urls)} links on the page to scrape.")
            except requests.RequestException as e:
                logger.error(f"Could not fetch the base URL for link extraction: {e}")
                return {"team_id": self.scraper.team_id, "items": [], "status": "fallback_failed"}

        if not all_urls:
            logger.error(f"No URLs found to scrape for {base_url}.")
            return {"team_id": self.scraper.team_id, "items": [], "status": "no_urls_found"}

        # --- Deduplication Step ---
        original_url_count = len(all_urls)
        # Convert to set to remove duplicates, then back to list
        unique_urls = list(set(all_urls))
        deduped_url_count = len(unique_urls)

        if original_url_count > deduped_url_count:
            duplicates_removed = original_url_count - deduped_url_count
            logger.info(f"Removed {duplicates_removed} duplicate URLs. Now scraping {deduped_url_count} unique URLs.")
        
        all_items = []
        base_domain = urlparse(base_url).netloc
        total_urls_to_scrape = len(unique_urls)

        for i, url in enumerate(unique_urls):
            if urlparse(url).netloc != base_domain:
                logger.info(f"Skipping URL from different domain: {url}")
                continue

            logger.info(f"({i+1}/{total_urls_to_scrape}) Scraping URL: {url}")
            try:
                result = self.scraper.scrape_with_ai_orchestration(url)
                if result and result.get("items"):
                    all_items.extend(result["items"])
                    logger.info(f"Successfully scraped {len(result['items'])} items from {url}")
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")

        logger.info(f"Crawl finished. Total items scraped: {len(all_items)}")
        return {
            "team_id": self.scraper.team_id,
            "items": all_items,
            "status": "crawl_completed"
        } 