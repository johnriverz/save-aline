#!/usr/bin/env python3
"""
Kadoa-Inspired AI Scraper
Core concepts: AI orchestration, self-healing, adaptive strategies
"""

import json
import time
import random
import logging
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import openai
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
from api_key_manager import get_openai_api_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KadoaInspiredScraper:
    """
    AI-orchestrated scraper inspired by Kadoa's approach:
    1. AI agents choose strategies
    2. Self-healing adaptation
    3. Automated data transformation
    """
    
    def __init__(self, team_id: str = "aline123"):
        self.team_id = team_id
        self.client = openai.OpenAI(api_key=get_openai_api_key())
        self.website_memory = {}  # Store what works for each site
    
    def scrape_with_ai_orchestration(self, url: str) -> Dict:
        """
        Main method: AI decides strategy, executes, learns from results
        """
        logger.info(f"🤖 AI Orchestration starting for: {url}")
        
        domain = urlparse(url).netloc
        attempts = []
        
        for attempt in range(3):
            # AI Agent 1: Strategy Selection
            strategy = self._ai_choose_strategy(url, attempts)
            logger.info(f"🎯 AI chose: {strategy['method']} - {strategy['reasoning']}")
            
            # Execute chosen strategy
            result = self._execute_strategy(url, strategy)
            
            if result and result.get('items'):
                # Success! Learn from it
                self._update_memory(domain, strategy['method'], True)
                logger.info(f"✅ Success with {strategy['method']}")
                return result
            else:
                # Failed, record and try again
                attempts.append({
                    'method': strategy['method'],
                    'success': False,
                    'attempt': attempt + 1
                })
                self._update_memory(domain, strategy['method'], False)
                logger.warning(f"❌ {strategy['method']} failed, trying next...")
        
        return {"team_id": self.team_id, "items": [], "status": "all_strategies_failed"}
    
    def _ai_choose_strategy(self, url: str, previous_attempts: List[Dict]) -> Dict:
        """
        AI Agent that chooses the best strategy based on context
        """
        domain = urlparse(url).netloc
        memory = self.website_memory.get(domain, {})
        
        context = f"""
Website: {url}
Domain: {domain}
Previous attempts: {previous_attempts}
Known successful methods: {memory.get('successful', [])}
Known failed methods: {memory.get('failed', [])}

Choose the best scraping strategy from:
1. simple_requests - Basic HTTP requests
2. headers_rotation - Rotate user agents and headers
3. browser_automation - Use Playwright browser
4. stealth_browser - Advanced anti-detection browser

Consider:
- interviewing.io likely has bot protection (use browser_automation or stealth_browser)
- nilmamano.com might be simpler (try headers_rotation first)
- If previous attempts failed, escalate to more sophisticated methods
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert web scraping strategist. Return only JSON with 'method' and 'reasoning' fields."},
                    {"role": "user", "content": context}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            # Clean up potential markdown formatting
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1]
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"AI strategy selection failed: {e}")
            # Fallback strategy
            return {
                "method": "browser_automation",
                "reasoning": "Fallback due to AI error"
            }
    
    def _execute_strategy(self, url: str, strategy: Dict) -> Optional[Dict]:
        """
        Execute the chosen strategy
        """
        method = strategy['method']
        
        if method == "simple_requests":
            return self._simple_requests(url)
        elif method == "headers_rotation":
            return self._headers_rotation(url)
        elif method == "browser_automation":
            return self._browser_automation(url)
        elif method == "stealth_browser":
            return self._stealth_browser(url)
        else:
            logger.error(f"Unknown method: {method}")
            return None
    
    def _simple_requests(self, url: str) -> Optional[Dict]:
        """Basic HTTP requests"""
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            response = session.get(url, timeout=15)
            response.raise_for_status()
            
            return self._ai_extract_content(response.text, url)
            
        except Exception as e:
            logger.error(f"Simple requests failed: {e}")
            return None
    
    def _headers_rotation(self, url: str) -> Optional[Dict]:
        """Rotate headers and user agents"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Human-like delay
            time.sleep(random.uniform(2, 4))
            
            response = session.get(url, timeout=15)
            response.raise_for_status()
            
            return self._ai_extract_content(response.text, url)
            
        except Exception as e:
            logger.error(f"Headers rotation failed: {e}")
            return None
    
    def _browser_automation(self, url: str) -> Optional[Dict]:
        """Use Playwright browser automation with surgical link extraction for known complex sites."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                page.goto(url, wait_until='networkidle')

                # Surgical extraction for the problematic "Company Guides" page
                if "topics#companies" in url:
                    logger.info("Applying surgical extraction for Company Guides...")
                    guide_links = page.evaluate("""() => {
                        const links = [];
                        const guideSections = document.querySelectorAll('h3');
                        guideSections.forEach(h3 => {
                            if (h3.textContent.includes('Company-specific guides')) {
                                let currentElement = h3.nextElementSibling;
                                while (currentElement && currentElement.tagName === 'A') {
                                    links.push({
                                        title: currentElement.textContent.trim(),
                                        url: currentElement.href
                                    });
                                    currentElement = currentElement.nextElementSibling;
                                }
                            }
                        });
                        return links;
                    }""")
                    
                    items = []
                    for link in guide_links:
                        items.append({
                            "title": link['title'],
                            "content": f"A company-specific interview guide for {link['title']}.",
                            "content_type": "blog",
                            "source_url": link['url'],
                            "author": "Unknown",
                            "user_id": ""
                        })
                    
                    browser.close()
                    return {"team_id": self.team_id, "items": items}

                # Fallback to general content extraction for other sites
                content = page.content()
                browser.close()
                
                return self._ai_extract_content(content, url)
                
        except Exception as e:
            logger.error(f"Browser automation failed: {e}")
            return None
    
    def _stealth_browser(self, url: str) -> Optional[Dict]:
        """Advanced stealth browser with anti-detection"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-first-run',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                )
                
                page = context.new_page()
                
                # Anti-detection
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                """)
                
                page.goto(url, wait_until='networkidle')
                time.sleep(random.uniform(3, 6))  # Human-like delay
                
                content = page.content()
                browser.close()
                
                return self._ai_extract_content(content, url)
                
        except Exception as e:
            logger.error(f"Stealth browser failed: {e}")
            return None
    
    def _ai_extract_content(self, html: str, url: str) -> Optional[Dict]:
        """
        AI Agent 2: Automated data transformation
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove scripts and styles
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            text = soup.get_text()
            # A more robust cleaning process
            text = ' '.join(text.split()) # Consolidate whitespace
            # Remove control characters except for standard whitespace
            text = ''.join(ch for ch in text if ch.isprintable() or ch in '\n\r\t')

            if len(text) < 100:
                return None
            
            # AI transforms raw HTML into the required structured data format
            system_prompt = """You are an expert data transformation agent. Your task is to extract the main article from the provided HTML content and format it into a specific JSON structure.

Return ONLY a valid JSON object with the following schema:
{
  "title": "The main title of the article. Be concise and accurate.",
  "content": "The full article content, formatted as clean Markdown (max 2000 chars). Preserve headings, lists, bold text, and code blocks.",
  "author": "The author's name, or 'Unknown' if not found."
}

Focus exclusively on the main article content. Ignore navigation bars, sidebars, ads, footers, and other boilerplate text. Ensure the content is well-structured and readable.
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"URL: {url}\n\nContent:\n{text[:4000]}"}
                ],
                max_tokens=1000,
                temperature=0.0
            )
            
            content = response.choices[0].message.content.strip()
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1]
            
            extracted = json.loads(content)
            
            # Ensure the output matches the required format exactly
            return {
                "team_id": self.team_id,
                "items": [
                    {
                        "title": extracted.get("title", "Extracted Content"),
                        "content": extracted.get("content", text[:2000]),
                        "content_type": "blog",
                        "source_url": url,
                        "author": extracted.get("author", "Unknown"),
                        "user_id": ""
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"AI content extraction failed: {e}")
            return None
    
    def _update_memory(self, domain: str, method: str, success: bool):
        """
        Self-healing: Update memory about what works for each domain
        """
        if domain not in self.website_memory:
            self.website_memory[domain] = {"successful": [], "failed": []}
        
        if success:
            if method not in self.website_memory[domain]["successful"]:
                self.website_memory[domain]["successful"].append(method)
            # Remove from failed if it's now working
            if method in self.website_memory[domain]["failed"]:
                self.website_memory[domain]["failed"].remove(method)
        else:
            if method not in self.website_memory[domain]["failed"]:
                self.website_memory[domain]["failed"].append(method)

def main():
    """Test the Kadoa-inspired scraper"""
    scraper = KadoaInspiredScraper()
    
    test_urls = [
        "https://interviewing.io/blog",
        "https://nilmamano.com/blog/category/dsa",
        "https://quill.co/blog"
    ]
    
    all_results = []
    
    for url in test_urls:
        print(f"\n🤖 Testing Kadoa-inspired AI scraper on: {url}")
        result = scraper.scrape_with_ai_orchestration(url)
        
        items_count = len(result.get('items', []))
        print(f"✅ Extracted {items_count} items")
        
        if result.get('items'):
            print(f"📄 Sample: {result['items'][0]['title'][:50]}...")
        
        all_results.append({
            'url': url,
            'result': result
        })
    
    # Save results
    with open('kadoa_inspired_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n🎉 Kadoa-inspired scraping complete!")
    print(f"📊 Results saved to kadoa_inspired_results.json")
    print(f"🧠 Website memory: {scraper.website_memory}")

if __name__ == "__main__":
    main() 