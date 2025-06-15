# Aline Technical Knowledge Base Scraper

This project is a flexible and extensible scraping framework designed to gather data from various sources to build a technical knowledge base for Aline's AI. It includes scrapers for blogs, company/interview guides, and local PDF documents.

The framework is designed to be highly modular, allowing for the easy addition of new scrapers without modifying the core application logic.

## Features

- **Dynamic Scraper Discovery**: Automatically discovers and registers new scraper "plugins" placed in the `scraper/scrapers` directory.
- **YAML Configuration**: Uses a clean, human-readable `config.yaml` file to manage scraper sources.
- **Interactive CLI**: A command-line interface to easily initialize, add, and remove scraper sources from the configuration.
- **Multi-Source Scraping**: Capable of scraping content from web pages (server-side and client-side rendered) and local PDF files.
- **Standardized Output**: Produces a consistent `output.json` file ready for ingestion by Aline's systems.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/johnriverz/save-aline
    cd save-aline
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\\Scripts\\activate`
    ```
    Install the required Python packages:
    ```bash
    pip install -r scraper/requirements.txt
    ```

3. **Install Playwright browsers:**
   The scraper for Nil's DS&A blog uses Playwright, which requires browser binaries.
   ```bash
   playwright install
   ```

## Usage

The primary way to interact with the scraper is through the `main.py` script, which provides a command-line interface.

### 1. Configure Scraper Sources

Before you can run the scraper, you need a `config.yaml` file. You can create a default one and then customize it.

**Initialize the Default Configuration**

This is the recommended first step. It creates a `scraper/config.yaml` file with all the required sources for the assignment.
```bash
python -m scraper.main config init
```

**Add a New Source (Optional)**

This command allows you to add a new scraping target to your configuration file by using one of the available **scraper plugins**. Note that a scraper plugin must exist first for the website you want to scrape (see the "Extending the Scraper" section below).
```bash
python -m scraper.main config add
```
The wizard will show you a list of available scraper plugins (e.g., "Quill.co Blog") and guide you through adding a new source to your `config.yaml`.

**Remove a Source (Optional)**

To remove a source from your configuration:
```bash
python -m scraper.main config remove
```
This will list the sources in your `config.yaml` and let you choose one to remove.

### 2. Run the Scraper

Once your `config.yaml` is ready, run the main scraping process:
```bash
python -m scraper.main
```
The script will:
- Log its progress to the console and to `scraper.log`.
- Scrape all sources defined in `scraper/config.yaml`.
- Create a final `scraper/output.json` file containing all the scraped data.

## Extending the Scraper (For Developers)

Adding a new scraper is simple:

1.  **Create a New Scraper File**: Add a new Python file in the `scraper/scrapers/` directory (e.g., `quill_blog_scraper.py`).

2.  **Implement the Scraper Class**: Inside your new file, create a class that inherits from `BaseScraper`.

    -   It **must** inherit from `scraper.scrapers.base_scraper.BaseScraper`.
    -   It **must** have a `name` class attribute. This name is used by the CLI to identify the scraper.
    -   It **must** implement a `scrape(self)` method that returns a list of dictionaries.
    -   For client-side rendered websites (like those built with React or Next.js), you **must** use a browser automation tool like Playwright, as shown in the example below.

3.  **Example Scraper (`quill_blog_scraper.py`):**
    ```python
    import logging
    from playwright.sync_api import sync_playwright, Error
    from urllib.parse import urljoin
    from .base_scraper import BaseScraper

    class QuillBlogScraper(BaseScraper):
        # This name will be shown in the `config add` wizard
        name = "Quill.co Blog"

        def __init__(self, url, selectors=None):
            super().__init__(url)
            self.selectors = selectors

        def scrape(self):
            # Your scraping logic here...
            logging.info(f"Scraping Quill.co blog from {self.url}")
            items = []
            # ... (Playwright logic to launch browser, scrape pages, etc.) ...
            return items
    ```

4.  **Import in `__init__.py`**: Add your new class to `scraper/scrapers/__init__.py` so it can be discovered.
    ```python
    # scraper/scrapers/__init__.py
    # ... other imports
    from .quill_blog_scraper import QuillBlogScraper
    ```

5.  **Add to Config**: Run `python -m scraper.main config add`. Your new scraper, "Quill.co Blog", will appear as an option. 