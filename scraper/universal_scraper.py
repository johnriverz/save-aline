import json
import os
import logging
import time
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import openai
from trafilatura import fetch_url, extract
from trafilatura.feeds import find_feed_urls
from trafilatura.sitemaps import sitemap_search
from api_key_manager import get_openai_api_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalBlogScraper:
    """
    Universal blog scraper that works for any blog using AI extraction.
    No site-specific code - uses intelligent discovery and LLM extraction.
    """
    
    def __init__(self, base_url: str, team_id: str = "aline123"):
        self.base_url = base_url
        self.team_id = team_id
        # Use smart API key management
        api_key = get_openai_api_key()
        self.client = openai.OpenAI(api_key=api_key)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; UniversalBlogScraper/1.0)'
        })
        
    def scrape(self) -> Dict:
        """
        Main scraping workflow: Discover → Extract → Format
        """
        logger.info(f"Starting universal scrape of: {self.base_url}")
        
        # Step 1: Auto-discover content URLs
        urls = self._discover_content_urls()
        logger.info(f"Discovered {len(urls)} URLs to scrape")
        
        # Step 2: Extract content from each URL
        items = []
        for url in urls[:20]:  # Limit for testing - remove in production
            try:
                item = self._extract_content(url)
                if item:
                    items.append(item)
                    logger.info(f"✅ Extracted: {item['title'][:50]}...")
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"❌ Failed to extract {url}: {e}")
                continue
                
        return {
            "team_id": self.team_id,
            "items": items
        }
    
    def _discover_content_urls(self) -> List[str]:
        """
        Auto-discover content URLs using multiple strategies:
        1. RSS/Atom feeds (most reliable)
        2. Sitemap.xml 
        3. Crawl fallback
        """
        urls = set()
        
        # Strategy 1: RSS/Atom feeds
        try:
            feed_urls = find_feed_urls(self.base_url)
            for feed_url in feed_urls:
                urls.update(self._extract_urls_from_feed(feed_url))
                logger.info(f"Found {len(urls)} URLs from RSS feed")
        except Exception as e:
            logger.warning(f"RSS discovery failed: {e}")
        
        # Strategy 2: Sitemap
        if len(urls) < 5:  # Only if RSS didn't find much
            try:
                sitemap_urls = sitemap_search(self.base_url)
                urls.update(sitemap_urls[:50])  # Limit sitemap URLs
                logger.info(f"Added {len(sitemap_urls)} URLs from sitemap")
            except Exception as e:
                logger.warning(f"Sitemap discovery failed: {e}")
        
        # Strategy 3: Crawl fallback (simple)
        if len(urls) < 3:
            try:
                crawled_urls = self._simple_crawl()
                urls.update(crawled_urls)
                logger.info(f"Added {len(crawled_urls)} URLs from crawling")
            except Exception as e:
                logger.warning(f"Crawl fallback failed: {e}")
        
        return list(urls)
    
    def _extract_urls_from_feed(self, feed_url: str) -> List[str]:
        """Extract article URLs from RSS/Atom feed"""
        try:
            response = self.session.get(feed_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'xml')
            
            urls = []
            # Handle both RSS and Atom formats
            for item in soup.find_all(['item', 'entry']):
                link = item.find('link')
                if link:
                    url = link.get('href') or link.text
                    if url:
                        urls.append(url)
            
            return urls
        except Exception as e:
            logger.error(f"Failed to parse feed {feed_url}: {e}")
            return []
    
    def _simple_crawl(self) -> List[str]:
        """Simple crawl of the main page to find blog post links"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            urls = set()
            # Look for common blog post link patterns
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(self.base_url, href)
                
                # Filter for likely blog post URLs
                if self._looks_like_blog_post(full_url):
                    urls.add(full_url)
            
            return list(urls)
        except Exception as e:
            logger.error(f"Simple crawl failed: {e}")
            return []
    
    def _looks_like_blog_post(self, url: str) -> bool:
        """Heuristics to identify blog post URLs"""
        url_lower = url.lower()
        
        # Include patterns
        blog_indicators = ['/blog/', '/post/', '/article/', '/news/', '/guide/']
        has_blog_indicator = any(indicator in url_lower for indicator in blog_indicators)
        
        # Exclude patterns
        exclude_patterns = ['/tag/', '/category/', '/author/', '/page/', '/feed', 
                           '/rss', '/xml', '/json', '/about', '/contact', '/privacy']
        has_exclude_pattern = any(pattern in url_lower for pattern in exclude_patterns)
        
        # Must be from the same domain
        same_domain = urlparse(url).netloc == urlparse(self.base_url).netloc
        
        return same_domain and (has_blog_indicator or not has_exclude_pattern)
    
    def _extract_content(self, url: str) -> Optional[Dict]:
        """
        Extract structured content from a URL using AI
        """
        # Step 1: Get clean article text
        try:
            downloaded = fetch_url(url)
            if not downloaded:
                return None
                
            clean_text = extract(downloaded, include_comments=False, include_tables=True)
            if not clean_text or len(clean_text) < 100:
                return None
                
        except Exception as e:
            logger.error(f"Failed to fetch/clean {url}: {e}")
            return None
        
        # Step 2: AI extraction
        try:
            extracted_data = self._ai_extract(clean_text, url)
            return extracted_data
        except Exception as e:
            logger.error(f"AI extraction failed for {url}: {e}")
            return None
    
    def _ai_extract(self, text: str, source_url: str) -> Dict:
        """
        Use GPT-4o-mini to extract structured data from article text
        """
        system_prompt = """You are a technical content analyzer. Extract structured data from blog posts and technical articles.

Always return valid JSON with these exact fields:
{
  "title": "string - the main title",
  "content": "string - the full article content in markdown format", 
  "content_type": "blog",
  "author": "string - author name or 'Unknown'",
  "publish_date": "string - date in YYYY-MM-DD format or null",
  "programming_languages": ["array", "of", "languages"],
  "frameworks_mentioned": ["array", "of", "frameworks"],
  "key_topics": ["array", "of", "key", "technical", "topics"]
}

Focus on extracting technical knowledge, code examples, and educational content."""

        user_prompt = f"""Extract metadata from this technical article:

<ARTICLE_URL>
{source_url}
</ARTICLE_URL>

<ARTICLE_TEXT>
{text[:8000]}  
</ARTICLE_TEXT>"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=2000
            )
            
            extracted = json.loads(response.choices[0].message.content)
            
            # Format to match required output structure
            return {
                "title": extracted.get("title", "Untitled"),
                "content": extracted.get("content", text[:1000]),  # Fallback to original text
                "content_type": "blog",
                "source_url": source_url,
                "author": extracted.get("author", "Unknown"),
                "user_id": ""
            }
            
        except Exception as e:
            logger.error(f"AI extraction error: {e}")
            # Fallback: return basic structure
            return {
                "title": "Unknown Title",
                "content": text[:1000],
                "content_type": "blog", 
                "source_url": source_url,
                "author": "Unknown",
                "user_id": ""
            }


def main():
    """CLI interface for the universal scraper"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Blog Scraper")
    parser.add_argument("url", help="Blog URL to scrape")
    parser.add_argument("--team-id", default="aline123", help="Team ID for output")
    parser.add_argument("--output", default="output.json", help="Output file")
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = UniversalBlogScraper(args.url, args.team_id)
    
    # Run scraping
    result = scraper.scrape()
    
    # Save output
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Scraped {len(result['items'])} items from {args.url}")
    print(f"📁 Output saved to {args.output}")


if __name__ == "__main__":
    main() 