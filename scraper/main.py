import json
import logging
import yaml
import pkgutil
import inspect
import argparse
import os
from importlib import import_module
from .scrapers.base_scraper import BaseScraper

# The default configuration, to be created with 'config init'
DEFAULT_CONFIG = {
    "sources": [
        {
            "name": "Interviewing.io Blog",
            "url": "https://interviewing.io/blog",
            "type": "blog",
            "selectors": {"next_data_script_id": "__NEXT_DATA__"}
        },
        {
            "name": "Interviewing.io Company Guides",
            "url": "https://interviewing.io/topics#companies",
            "type": "guide",
            "selectors": {
                "guide_url_pattern": "-interview-questions",
                "title_selector": "h1",
                "content_container_selector": "div.shrink",
                "content_element_selectors": ["h2", "h3", "p", "li"]
            }
        },
        {
            "name": "Interviewing.io Interview Guides",
            "url": "https://interviewing.io/learn#interview-guides",
            "type": "guide",
            "selectors": {
                "section_header_id": "interview-guides",
                "guides_container_selector": "div",
                "guide_link_selector": "a",
                "title_selector": "h3",
                "content_selector": "p"
            }
        },
        {
            "name": "Nil's DS&A Blog",
            "url": "https://nilmamano.com/blog/category/dsa",
            "type": "blog"
        },
        {
            "name": "BCTCI - First 7 Chapters",
            "url": "scraper/Sneak Peek BCTCI - First 7 Chapters - What's Broken About Coding Interviews, What Recruiters Won't Tell You, How to Get In the Door, and more.pdf",
            "type": "pdf"
        },
        {
            "name": "BCTCI - Sliding Windows & Binary Search",
            "url": "scraper/Sneak Peak BCTCI - Sliding Windows & Binary Search.pdf",
            "type": "pdf"
        }
    ]
}

CONFIG_PATH = 'scraper/config.yaml'

def discover_scrapers(package):
    """
    Dynamically discover and register scraper classes from a given package.
    """
    scraper_map = {}
    package_path = package.__path__
    package_name = package.__name__

    for _, module_name, _ in pkgutil.walk_packages(package_path, prefix=f"{package_name}."):
        module = import_module(module_name)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Register classes that are subclasses of BaseScraper but not BaseScraper itself
            if issubclass(obj, BaseScraper) and obj is not BaseScraper:
                # Use a more descriptive name if available, otherwise class name
                scraper_name = getattr(obj, 'name', name)
                scraper_map[scraper_name] = obj
    return scraper_map

def config_init():
    """Creates a default config.yaml file."""
    if os.path.exists(CONFIG_PATH):
        overwrite = input(f"'{CONFIG_PATH}' already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Initialization cancelled.")
            return
    
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(DEFAULT_CONFIG, f, sort_keys=False, indent=2)
    print(f"Successfully created default configuration at '{CONFIG_PATH}'.")

def config_add(scraper_map):
    """Interactively adds a new source to the config file."""
    print("--- Add a New Scraper Source ---")
    
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = {'sources': []}

    # Display available scrapers
    scraper_names = list(scraper_map.keys())
    for i, name in enumerate(scraper_names):
        print(f"[{i+1}] {name}")
    
    try:
        selection = int(input("Select a scraper to add: ")) - 1
        if not (0 <= selection < len(scraper_names)):
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input.")
        return

    selected_name = scraper_names[selection]
    scraper_class = scraper_map[selected_name]
    
    source_config = {}
    
    # Handle PDF scraper as a special case for naming
    if selected_name == "PDF Scraper":
        source_config['name'] = input("Enter a descriptive name for this PDF source: ")
        source_config['url'] = input("Enter the relative file path for the PDF: ")
        source_config['type'] = 'pdf'
    else:
        source_config['name'] = selected_name
        source_config['url'] = input(f"Enter the full URL for {selected_name}: ")

    if 'selectors' in scraper_class.__init__.__code__.co_varnames:
        print("This scraper may require selectors. Adding a placeholder.")
        source_config['selectors'] = {}

    config['sources'].append(source_config)
    
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, sort_keys=False, indent=2)
    print(f"Successfully added '{source_config['name']}' to '{CONFIG_PATH}'.")

def config_remove():
    """Interactively removes a source from the config file."""
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Configuration file '{CONFIG_PATH}' not found.")
        return
        
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    print("--- Remove a Scraper Source ---")
    sources = config.get('sources', [])
    if not sources:
        print("No sources to remove.")
        return

    for i, source in enumerate(sources):
        print(f"[{i+1}] {source['name']}")
        
    try:
        selection = int(input("Select a source to remove: ")) - 1
        if not (0 <= selection < len(sources)):
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input.")
        return
        
    removed_source = sources.pop(selection)
    
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, sort_keys=False, indent=2)
        
    print(f"Successfully removed '{removed_source['name']}' from '{CONFIG_PATH}'.")

def main():
    """
    Main function to run the scraper or manage config.
    """
    parser = argparse.ArgumentParser(description="Aline Web Scraper & Config Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # 'config' command
    config_parser = subparsers.add_parser('config', help='Manage the configuration file.')
    config_subparsers = config_parser.add_subparsers(dest='config_command', required=True)
    
    # 'config init' command
    config_subparsers.add_parser('init', help="Create a default config.yaml.")
    # 'config add' command
    config_subparsers.add_parser('add', help="Add a new source to config.yaml.")
    # 'config remove' command
    config_subparsers.add_parser('remove', help="Remove a source from config.yaml.")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Discover scrapers automatically from the .scrapers package
    from . import scrapers
    scraper_map = discover_scrapers(scrapers)

    if args.command == 'config':
        if args.config_command == 'init':
            config_init()
        elif args.config_command == 'add':
            config_add(scraper_map)
        elif args.config_command == 'remove':
            config_remove()
        return

    logging.info(f"Discovered scrapers: {', '.join(scraper_map.keys())}")

    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file ('{CONFIG_PATH}') not found.")
        logging.info("Create a default config using: python -m scraper.main config init")
        return

    output_data = []

    for source in config.get('sources', []):
        logging.info(f"Processing source: {source['name']}")
        
        scraper_class = None
        # Handle PDF scraping as a special case based on type
        if source.get('type') == 'pdf':
            scraper_class = scraper_map.get("PDF Scraper")
        else:
            # For other types, find scraper by its registered name
            scraper_class = scraper_map.get(source['name'])

        if scraper_class:
            try:
                # Pass selectors only if the scraper's __init__ expects it
                if 'selectors' in scraper_class.__init__.__code__.co_varnames:
                    scraper = scraper_class(source['url'], selectors=source.get('selectors'))
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
            except Exception as e:
                logging.error(f"Failed to scrape {source['name']}: {e}", exc_info=True)
        else:
            logging.warning(f"No scraper found for source: {source['name']}")

    # The final output will be written to a file here.
    with open('scraper/output.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    logging.info("Scraping complete. Output saved to scraper/output.json")

if __name__ == '__main__':
    main()
