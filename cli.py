import argparse
import os
import sys
import json

# Add scraper directory to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from agent_scraper import KadoaInspiredScraper
from pdf_processor import PDFProcessor
from api_key_manager import APIKeyManager
from scraper.crawler import Crawler

def scrape_pdf(file_path: str, output_path: str):
    """Scrapes a single PDF file and saves the result to a file."""
    print(f"📖 Scraping PDF: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at {file_path}")
        return
        
    processor = PDFProcessor()
    # Extract title from the filename
    title = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ").title()
    
    items = processor.process_pdf(pdf_path=file_path, title=title)
    
    if items:
        # The output from PDF processor is a list of items, but the standard format is a dictionary
        # containing the team_id and the items list.
        data = {
            "team_id": "aline123", # Default team_id
            "items": items
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"✅ Results saved to {output_path}")
    else:
        print(f"❌ Scraping failed for {file_path}. No data was extracted.")

def crawl_site(url: str, output_path: str):
    """Crawls an entire website and saves all scraped data."""
    print(f"🚀 Starting full site crawl for: {url}")
    
    crawler = Crawler()
    data = crawler.crawl(url)
    
    if data and data.get("items"):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"✅ Crawl finished. Scraped {len(data['items'])} items.")
        print(f"Results saved to {output_path}")
    else:
        print(f"❌ Crawling failed for {url}. Reason: {data.get('status', 'Unknown error')}")

def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(description="Aline Web Scraper CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scrape PDF command
    parser_pdf = subparsers.add_parser("scrape_pdf", help="Scrape a single PDF file")
    parser_pdf.add_argument("file_path", type=str, help="The local path to the PDF file")
    parser_pdf.add_argument("--output", type=str, default="scraped_data.json", help="Path to save the output JSON file")

    # Crawl site command
    parser_crawl = subparsers.add_parser("crawl_site", help="Crawl and scrape an entire website starting from a base URL")
    parser_crawl.add_argument("url", type=str, help="The base URL of the website to crawl")
    parser_crawl.add_argument("--output", type=str, default="crawled_data.json", help="Path to save the output JSON file")

    # API key command
    parser_api_key = subparsers.add_parser("set_api_key", help="Set and store the OpenAI API key")
    parser_api_key.add_argument("api_key", type=str, help="Your OpenAI API key")

    args = parser.parse_args()

    api_key_manager = APIKeyManager()

    if args.command == "scrape_pdf":
        if not api_key_manager.get_api_key():
            print("OpenAI API key not found. Please set it using the 'set_api_key' command.")
            return
        scrape_pdf(args.file_path, args.output)
    elif args.command == "crawl_site":
        if not api_key_manager.get_api_key():
            print("OpenAI API key not found. Please set it using the 'set_api_key' command.")
            return
        crawl_site(args.url, args.output)
    elif args.command == "set_api_key":
        api_key_manager.set_api_key(args.api_key)
        print("API key has been set successfully.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()