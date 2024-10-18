import pandas as pd
import requests
from bs4 import BeautifulSoup
import re  # Import regular expressions for citation removal
from io import StringIO
from typing import Dict, List, Tuple



class WikiYoinker:
    def __init__(self, starting_page_name: str = "Szeged", language_code: str = "hu") -> None:
        self.starting_page_name = starting_page_name
        self.language_code = language_code

    def yoink_page(self, url: str) -> tuple[list[pd.DataFrame], list[str]]:
        """This function should get the whole page and separate tables and the page text as return"""
        
        response = requests.get(url)
        tables: list[pd.DataFrame] = pd.read_html(StringIO(response.text))
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find_all(['p'])
        text = "\n".join([tag.get_text(strip=False) for tag in content])
        sentences = re.sub(r'\[\d+\]', '', text).strip().replace("\n", " ").replace("  ", " ").split(". ")
        return tables, [s.strip() for s in sentences]

    def get_next_page(self) -> requests.Request:
        api_url = f"https://{self.language_code}.wikipedia.org/w/api.php"

        def get_next_page(apfrom: str):
            return apfrom

        S = requests.Session()

        PARAMS = {
            "action": "query",
            "format": "json",
            "list": "allpages",
            "apfrom": get_next_page(self.starting_page_name),
            "aplimit": 2,
        }


        R = S.get(url=api_url, params=PARAMS)
        DATA = R.json()
        PAGES = DATA["query"]["allpages"][0]["title"]
        self.starting_page_name = DATA["query"]["allpages"][1]["title"]

        page_url = f"https://hu.wikipedia.org/wiki/{PAGES}"

        request = requests.get(page_url)
        return request

    def extract_tables_by_h2(self, url: str) -> Dict[str, List[pd.DataFrame]]:
        # Fetch the response
        response = requests.get(url)

        # Split the response into chunks by <h2> sections
        sections = response.text.split('<h2')

        # Dictionary to store tables by section id
        tables_by_section = {}

        for section in sections[1:]:  # Skip the first chunk since it is before the first <h2>
            section = '<h2' + section  # Prepend <h2> to the section again

            # Find the ID of the <h2> tag, assuming format <h2 id="section_id">
            id_start = section.find('id="') + len('id="')
            id_end = section.find('"', id_start)
            section_id = section[id_start:id_end]  # Extract the id of the <h2> tag

            # Find the end of the <h2> tag
            end_of_h2 = section.find('</h2>') + len('</h2>')

            # Extract the part of the section after the <h2> header
            section_content = section[end_of_h2:]

            # Attempt to extract tables from the current section
            try:
                tables = pd.read_html(StringIO(section_content), decimal=",", thousands=" ")
                for table in tables:
                    table = table.map(lambda x: str(x).replace('.', ',') if isinstance(x, (int, float, str)) else x)
                tables_by_section[section_id] = tables  # Store tables under the section id
            except ValueError:
                # If no tables were found in this section, continue
                continue

        return tables_by_section

    def extract_paragraphs_by_h2(self, url: str) -> Dict[str, str]:
        # Fetch the response
        response = requests.get(url)

        # Split the response into chunks by <h2> sections
        sections = response.text.split('<h2')

        # Dictionary to store paragraphs by section id
        paragraphs_by_section = {}

        for section in sections[1:]:  # Skip the first chunk since it is before the first <h2>
            section = '<h2' + section  # Prepend <h2> to the section again

            # Find the ID of the <h2> tag
            id_start = section.find('id="') + len('id="')
            id_end = section.find('"', id_start)
            section_id = section[id_start:id_end]  # Extract the id of the <h2> tag

            # Find the end of the <h2> tag
            end_of_h2 = section.find('</h2>') + len('</h2>')

            # Extract the part of the section after the <h2> header
            section_content = section[end_of_h2:]

            # Extract <p> tags
            paragraphs = []
            while True:
                p_start = section_content.find('<p')
                if p_start == -1:
                    break  # No more <p> tags

                p_end = section_content.find('</p>', p_start) + len('</p>')
                paragraph = section_content[p_start:p_end]  # Extract the <p> tag content
                paragraphs.append(paragraph)

                # Remove the processed paragraph from section_content
                section_content = section_content[p_end:]

            # Unite paragraphs into plain text
            plain_text = ' '.join(paragraphs).replace('<p>', '').replace('</p>', '').strip()
            paragraphs_by_section[section_id] = plain_text  # Store plain text under the section id

        return paragraphs_by_section

    def find_matching_words(self, paragraph: str, table: pd.DataFrame) -> List[Dict[str, Tuple[int, int, str]]]:
        """ FIXME takes a paragraph string and a Pandas DataFrame as input and returns a list of coordinate/sentence pairs where words from the DataFrame match words in the paragraph."""
        # Preprocess the paragraph to get sentences and words
        sentences = re.split(r'(?<=[.!?]) +', paragraph)  # Split paragraph into sentences
        # Create a set of words in the paragraph for exact matching
        words_in_paragraph = set(re.findall(r'\b\w+\b', paragraph.lower()))  

        # Store results
        results = []

        # Check each cell in the DataFrame
        for i, row in table.iterrows():
            for j, cell in enumerate(row):
                # Normalize the cell and check for exact matches
                cell_str = str(cell).strip().lower()

                # Check if the cell itself is an exact match with any sentence
                if cell_str in [s.lower() for s in sentences]:
                    for sentence in sentences:
                        if sentence.lower() == cell_str:
                            results.append({
                                'cell_coordinates': (i, j),
                                'matching_sentence': sentence
                            })
        return results

if __name__ == "__main__":
    wikiyoinker = WikiYoinker()
    for x in range(1):
        req = wikiyoinker.get_next_page()
        tables = wikiyoinker.extract_tables_by_h2(req.url)
        paragraphs = wikiyoinker.extract_paragraphs_by_h2(req.url)
        for table in tables["Éghajlata"]:
            print(table)            
            results = wikiyoinker.find_matching_words(paragraphs['Éghajlata'], table)
            for result in results:
                row, col = result['cell_coordinates']  # Extract row and column coordinates
                word = table.iat[row, col]  
                print(f"{word}\t{result['matching_sentence']}")
