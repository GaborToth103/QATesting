import wikipediaapi
import requests
from bs4 import BeautifulSoup

def get_wikipedia_sections_and_tables(page_name):
    # Initialize Wikipedia API
    wiki = wikipediaapi.Wikipedia("gabor.toth.103@gmail.com", 'hu')
    page = wiki.page(page_name)

    if not page.exists():
        print(f"The page '{page_name}' does not exist.")
        return

    # Store the sections and tables in a dictionary
    h2_sections_with_tables = {}

    # Function to extract sections by level (for h2 level)
    def extract_sections(sections, level=1):
        for section in sections:
            if level == 2:
                h2_sections_with_tables[section.title] = {
                    "text": section.text,
                    "tables": []
                }
            extract_sections(section.sections, level + 1)

    # Extract h2 sections
    extract_sections(page.sections)

    # Fetch the full page HTML for table extraction
    response = requests.get(page.fullurl)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract tables and map them to h2 sections
    for section_title in h2_sections_with_tables:
        section_anchor = soup.find('span', id=section_title.replace(' ', '_'))

        if section_anchor:
            section_content = section_anchor.find_parent().find_next_sibling()

            while section_content and section_content.name != 'h2':
                # If we find a table in this section, extract it
                if section_content.name == 'table':
                    table_html = str(section_content)
                    h2_sections_with_tables[section_title]["tables"].append(table_html)

                section_content = section_content.find_next_sibling()

    return h2_sections_with_tables

# Test the function with a page name
page_name = "Szeged"
sections_with_tables = get_wikipedia_sections_and_tables(page_name)

# Print the extracted sections and tables
for h2, content in sections_with_tables.items():
    print(f"=== {h2} ===\n{content['text']}\n")
    for i, table in enumerate(content["tables"], 1):
        print(f"--- Table {i} in {h2} section ---")
        print(table)
        print("\n")
