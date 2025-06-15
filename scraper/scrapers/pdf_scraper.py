import PyPDF2
from .base_scraper import BaseScraper
import logging
import os

class PdfScraper(BaseScraper):
    """
    Scrapes text content from a PDF file.
    """
    name = "PDF Scraper" # This is a generic name

    def __init__(self, url, selectors=None):
        super().__init__(url)
        self.file_path = url # The 'url' from config is a file path
        self.selectors = selectors

    def scrape(self):
        """
        Scrape content from a PDF file.
        Extracts text from the PDF.
        """
        items = []
        try:
            with open(self.file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                content = ""
                
                num_pages_to_scrape = self.selectors.get("num_pages") if self.selectors else len(reader.pages)
                
                for i, page in enumerate(reader.pages):
                    if i >= num_pages_to_scrape:
                        break
                    content += page.extract_text() or ""
            
            # For a PDF book, we'll create one item with the full content
            file_name = os.path.basename(self.file_path)
            title = os.path.splitext(file_name)[0].replace("_", " ")

            items.append({
                "title": title,
                "content": content,
                "content_type": "book",
                "source_url": self.file_path,
                "author": "Aline", # Assuming author
                "user_id": ""
            })

        except FileNotFoundError:
            logging.error(f"Error: The file was not found at {self.file_path}")
            return []
        except Exception as e:
            logging.error(f"An error occurred while reading the PDF: {e}")
            return []
            
        return items 