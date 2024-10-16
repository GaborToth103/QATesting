import pandas as pd
import requests
from bs4 import BeautifulSoup
import re  # Import regular expressions for citation removal
from io import StringIO

import wikipediaapi

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

    def get_all_wiki_pages(self, languge_code: str = "hu") -> list[str]:
        """Gets all wikipedia pages within the certain language code.

        Args:
            languge_code (str, optional): The language code for the countries. Defaults to "hu".

        Returns:
            list[str]: list of all wikipedia pages for one specific language
        """
        def print_categorymembers(categorymembers, level=0, max_level=1):
                for c in categorymembers.values():
                    print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
                    if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
                        print_categorymembers(c.categorymembers, level=level + 1, max_level=max_level)


        wiki_wiki = wikipediaapi.Wikipedia('MyProjectName (gabor.toth.103@gmail.com)', language=languge_code)
        asd = wiki_wiki.page("Category:Physics")
        print("Category members: Category:Physics")
        print(asd, type(asd))
        exit()


        print_categorymembers(asd.categorymembers, "asd")
        list_of_pages: list[str] = []
        raise NotImplementedError()
        return list_of_pages

if __name__ == "__main__":
    wikiyoinker = WikiYoinker()
    tables, sentences = wikiyoinker.yoink_page("Szeged")
    for table in tables:
        print(table)
    wikiyoinker.get_all_wiki_pages()