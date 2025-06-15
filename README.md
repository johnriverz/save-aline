# Aline's Technical Knowledge Importer

This project contains a set of scripts to scrape technical content from various web sources and PDF files and compile it into a structured JSON format for use in a knowledge base.

## Project Structure

```
.
├── scraper/
│   ├── __init__.py
│   ├── config.json         # Configuration for data sources
│   ├── main.py             # Main script to run all scrapers
│   ├── output.json         # The final JSON output
│   ├── requirements.txt    # Python dependencies
│   └── scrapers/
│       ├── __init__.py
│       ├── base_scraper.py
│       ├── interviewing_io_blog_scraper.py
│       ├── interviewing_io_company_guides_scraper.py
│       ├── interviewing_io_interview_guides_scraper.py
│       ├── nils_dsa_blog_scraper.py
│       └── pdf_scraper.py
└── Save Aline Assignment.pdf
```

## Setup and Installation

1.  **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install Python dependencies:**
    It is recommended to use a virtual environment.
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r scraper/requirements.txt
    ```

3.  **Install Playwright browsers:**
    The scraper for Nil's DS&A Blog uses Playwright, which requires browser binaries.
    ```sh
    playwright install
    ```

## Configuration

All data sources are configured in `scraper/config.json`. You can add, remove, or modify sources in this file.

Each source has the following properties:
-   `name`: A human-readable name for the source. This is used to map to the correct scraper class in `main.py`.
-   `url`: The URL for web pages or the file path for local files (like PDFs).
-   `type`: The type of content (e.g., `blog`, `guide`, `pdf`).

## How to Run

To run the entire scraping process, execute the `main.py` script from the root directory:
```sh
python scraper/main.py
```
The script will process all enabled sources in `config.json` and generate the final output in `scraper/output.json`.

## Extending the Scraper

To add a new scraper for a new source:
1.  Create a new scraper class in a new file inside the `scraper/scrapers/` directory. Your new class should inherit from `BaseScraper`.
2.  Implement the `scrape` method to extract the required data.
3.  Import your new scraper class in `scraper/scrapers/__init__.py`.
4.  Add the new scraper to the `scraper_map` in `scraper/main.py`, mapping its name to the class.
5.  Add the new source's details to the `scraper/config.json` file. 