# Aline AI Scraper & Crawler

An intelligent, AI-powered web scraper and crawler designed to extract structured data from websites and PDF documents for Aline's knowledge base.

This tool uses a multi-layered approach, including an AI-orchestrator to choose the best scraping strategy (from simple requests to full browser automation) and another AI agent to transform raw content into clean, structured JSON.

## Features

-   **AI-Powered Scraping:** Dynamically selects the best strategy to bypass protections and extract data reliably.
-   **Full-Site Crawling:** Can crawl an entire website, discovering pages via sitemaps or on-page links.
-   **Intelligent Scoping:** Limits crawling to relevant sections of a website (e.g., only scraping `/blog/` pages).
-   **PDF Processing:** Extracts and structures content from local PDF files.
-   **User-Friendly CLI:** A simple and powerful command-line interface to control the scraper.

## Getting Started

### Prerequisites

-   Python 3.8+
-   An OpenAI API Key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ogToolTask
    ```

2.  **Set up a virtual environment and install dependencies:**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Install requirements
    pip install -r requirements.txt
    ```

3.  **Install Playwright browsers:**
    The scraper uses Playwright for browser automation. You need to install its required browsers.
    ```bash
    playwright install
    ```

4.  **Set Your API Key:**
    The scraper requires an OpenAI API key. You can set it once using the CLI:
    ```bash
    python cli.py set_api_key YOUR_OPENAI_API_KEY
    ```

## Usage

The tool is controlled via `cli.py`. Here are the available commands:

### Crawl an Entire Website
Crawls a website starting from a base URL, scraping all discovered pages. The crawl can be scoped by path. For example, providing a URL like `https://example.com/blog` will focus the crawl on pages within the `/blog/` directory.
```bash
python cli.py crawl_site "https://example.com/blog" --output crawled_site.json
```

### Scrape a PDF File
Extracts structured content from a local PDF document.
```bash
python cli.py scrape_pdf "path/to/your/document.pdf" --output document.json
```

## How It Works

This project is more than just a simple scraper. It uses a `Crawler` to discover URLs and an `agent_scraper` to process them. The `agent_scraper` contains two AI agents:

1.  **Strategy Agent:** Chooses the best method to fetch web content (simple request, header rotation, or full browser automation).
2.  **Extraction Agent:** Takes the raw HTML and transforms it into a clean, structured JSON output, following a stateless approach to ensure accuracy.

This design makes the tool resilient to anti-scraping measures and capable of handling complex data extraction tasks.
