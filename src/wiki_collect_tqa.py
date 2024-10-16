import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from io import StringIO

MINIMUM_TABLE_SIZE = 4

class WikiYoinker:
    def __init__(self, url: str = "https://hu.wikipedia.org/wiki/") -> None:
        self.url = url

    def yoink_page(self, page_name: str) -> tuple[list[pd.DataFrame], list[str]]:
        """This function should get the whole page and separate tables and the page text as return"""
        
        url = self.url + page_name
        response = requests.get(url)
        tables: list[pd.DataFrame] = pd.read_html(StringIO(response.text))
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find_all(['p'])
        text = "\n".join([tag.get_text(strip=False) for tag in content])
        sentences = re.sub(r'\[\d+\]', '', text).strip().replace("\n", " ").replace("  ", " ").split(". ")
        return tables, [s.strip() for s in sentences]

if __name__ == "__main__":
    wikiyoinker = WikiYoinker()
    tables, sentences = wikiyoinker.yoink_page("Szeged")
    for table in tables:
        if table.shape[0]*table.shape[1] > MINIMUM_TABLE_SIZE:
            print(table)
