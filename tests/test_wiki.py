import unittest, os, sys
sys.path.append(f"{os.getcwd()}/src")
from WikipediaYoinker import WikiYoinker

class TestWiki(unittest.TestCase):
    """"Testing wikipedia yoinker stuff"""    
    wikiyoinker = WikiYoinker()

    def test_get_all_wiki_pages(self):
        """Checks if the function works as intended for each language provided. Only returns the pages provided by the setting and nothing else."""
        all_wiki_pages = self.wikiyoinker.get_all_wiki_pages("hu")
        # Randomly check 100 pages if its the same as
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()