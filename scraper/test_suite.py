import json
import logging
from agent_scraper import KadoaInspiredScraper
from pdf_processor import PDFProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_test_suite():
    """
    Runs a comprehensive but fast test suite on all required sources.
    Limits each source to 3 items to ensure speed.
    """
    scraper = KadoaInspiredScraper()
    pdf_processor = PDFProcessor()
    
    test_sources = [
        {"type": "url", "source": "https://interviewing.io/blog", "name": "Interviewing.io Blog"},
        {"type": "url", "source": "https://interviewing.io/topics#companies", "name": "Company Guides"},
        {"type": "url", "source": "https://interviewing.io/learn#interview-guides", "name": "Interview Guides"},
        {"type": "url", "source": "https://nilmamano.com/blog/category/dsa", "name": "Nil's DS&A Blog"},
        {"type": "url", "source": "https://quill.co/blog", "name": "Quill.co Blog (Test Case)"},
        {"type": "pdf", "source": "scraper/Sneak Peek BCTCI - First 7 Chapters - What's Broken About Coding Interviews, What Recruiters Won't Tell You, How to Get In the Door, and more.pdf", "name": "Book: First 7 Chapters"},
        {"type": "pdf", "source": "scraper/Sneak Peak BCTCI - Sliding Windows & Binary Search.pdf", "name": "Book: Sliding Windows"}
    ]

    all_results = []
    limit = 3

    print("🚀 Starting Aline's Test Suite (Fast Mode)...")
    print("="*50)

    for source in test_sources:
        logger.info(f"Testing source: {source['name']}")
        try:
            if source['type'] == 'url':
                result = scraper.scrape_with_ai_orchestration(source['source'])
                # We can't easily limit the items from the AI scraper without modifying it,
                # but it's already fast as it only scrapes the main page.
            elif source['type'] == 'pdf':
                items = pdf_processor.process_pdf(source['source'], source['name'], max_chunks=limit)
                result = {
                    "team_id": "aline123",
                    "items": items
                }
            
            items_extracted = len(result.get('items', []))
            if items_extracted > 0:
                status = "✅ Success"
            else:
                status = "⚠️ Failed (No items extracted)"

            logger.info(f"{status} - Extracted {items_extracted} items from {source['name']}")
            all_results.append({
                "source": source['name'],
                "status": status,
                "items_count": items_extracted,
                "sample_item": result.get('items', [{}])[0].get('title', 'N/A')
            })

        except Exception as e:
            logger.error(f"❌ Critical Failure for {source['name']}: {e}")
            all_results.append({
                "source": source['name'],
                "status": "❌ Critical Failure",
                "error": str(e)
            })

    print("\n\n📋 Test Suite Summary:")
    print("="*50)
    for res in all_results:
        print(f"- {res['source']:<30} | {res['status']:<30} | Items: {res.get('items_count', 'N/A')}")

    with open('test_suite_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)

    print("\n\n💾 Full results saved to 'test_suite_results.json'")


if __name__ == "__main__":
    run_test_suite() 