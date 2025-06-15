from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    """
    def __init__(self, url):
        self.url = url

    @abstractmethod
    def scrape(self):
        """
        Scrape the content from the given URL.
        This method must be implemented by all subclasses.
        """
        pass
