import json
import logging
from .scrapers import (
    InterviewingIoBlogScraper, 
    NilsDsaBlogScraper,
    InterviewingIoCompanyGuidesScraper,
    InterviewingIoInterviewGuidesScraper,
    PdfScraper
)

# A mapping of source names to scraper classes
scraper_map = {
    "Interviewing.io Blog": InterviewingIoBlogScraper,
    "Nil's DS&A Blog": NilsDsaBlogScraper,
    "Interviewing.io Company Guides": InterviewingIoCompanyGuidesScraper,
    "Interviewing.io Interview Guides": InterviewingIoInterviewGuidesScraper,
    "Aline's Book (PDF)": PdfScraper
}

def main():
    """
    Main function to run the scraper.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("scraper.log"),
            logging.StreamHandler()
        ]
    )

    with open('scraper/config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    output_data = []

    for source in config['sources']:
        logging.info(f"Processing source: {source['name']}")
        
        # Determine the correct scraper class
        scraper_class = None
        if source['type'] == 'pdf':
            scraper_class = PdfScraper
        elif source['name'] in scraper_map:
            scraper_class = scraper_map[source['name']]

        if scraper_class:
            selectors = source.get('selectors')
            # Pass selectors only if the scraper's __init__ expects it
            if 'selectors' in scraper_class.__init__.__code__.co_varnames:
                 scraper = scraper_class(source['url'], selectors=selectors)
            else:
                 scraper = scraper_class(source['url'])
            
            items = scraper.scrape()
            if items:
                logging.info(f"Successfully scraped {len(items)} items from {source['name']}.")
                source_output = {
                    "team_id": "aline123",
                    "items": items
                }
                output_data.append(source_output)
            else:
                logging.warning(f"No items scraped from {source['name']}.")
        else:
            logging.warning(f"No scraper found for source: {source['name']}")

    # The final output will be written to a file here.
    with open('scraper/output.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    logging.info("Scraping complete. Output saved to scraper/output.json")

if __name__ == '__main__':
    main()
