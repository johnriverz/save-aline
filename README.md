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
    git clone <your-repo-url>
    cd <your-repo-directory>
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

If you write a new scraper plugin, you can add it to your configuration interactively.
```bash
python -m scraper.main config add
```
The wizard will show you a list of available scraper plugins and guide you through adding a new source to your `config.yaml`.

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

1.  **Create a New Scraper File**: Add a new Python file in the `scraper/scrapers/` directory (e.g., `my_new_scraper.py`).

2.  **Implement the Scraper Class**: Inside your new file, create a class that inherits from `BaseScraper`.

    -   It **must** inherit from `scraper.scrapers.base_scraper.BaseScraper`.
    -   It **must** have a `name` class attribute. This name is used by the CLI to identify the scraper.
    -   It **must** implement a `scrape(self)` method that returns a list of dictionaries, where each dictionary represents a scraped item.

3.  **Example Scraper (`my_new_scraper.py`):**
    ```python
    from .base_scraper import BaseScraper

    class MyNewScraper(BaseScraper):
        # This name will be shown in the `config add` wizard
        name = "My Awesome Blog"

        def __init__(self, url, selectors=None):
            super().__init__(url)
            self.selectors = selectors

        def scrape(self):
            # Your scraping logic here...
            print(f"Scraping from {self.url}!")
            # Must return a list of items
            return [
                {
                    "title": "My First Post",
                    "content": "This is the content.",
                    "content_type": "blog",
                    "source_url": self.url,
                    "author": "Me",
                    "user_id": ""
                }
            ]
    ```

4.  **Import in `__init__.py`**: Add your new class to `scraper/scrapers/__init__.py` so it can be discovered.
    ```python
    # scraper/scrapers/__init__.py
    # ... other imports
    from .my_new_scraper import MyNewScraper
    ```

5.  **Add to Config**: Run `python -m scraper.main config add` and your new scraper, "My Awesome Blog", will appear as an option. 