import pandas as pd
import re
import sys
import os
sys.path.append(f"{os.getcwd()}/src")
import unittest
from WikipediaYoinker import WikiYoinker, Section

class TestWikiYoinker(unittest.TestCase):        
    wikiyoinker = WikiYoinker()
    
    def test_transform_statement_to_question(self):        
        pairs = [
            ("Őt Gábornak hívják!", "Gábornak"),
            ("A labda piros.", "piros"),
            ("11.2 az átlagos hőmérséklet.", "11.2")
        ]
        for pair in pairs:
            question = self.wikiyoinker.transform_statement_to_question(*pair)
            print(question)
            self.assertEqual(type(question), str)
            self.assertEqual(question[-1], "?")
            self.assertNotIn("<mask>", question)
            self.assertNotIn(pair[1], question)
            
    def test_get_500_pages(self):
        # TODO
        the_list = self.wikiyoinker.get_next_500_page()
        self.assertEqual(len(the_list), 500)
        for url in the_list:
            self.assertTrue(url)

    def test_extract_tables_by_h2(self):
        # TODO
        
        urls = [
            "https://hu.wikipedia.org/wiki/Szeged"
        ]
        
        for url in urls:
            self.wikiyoinker.extract_tables_by_h2(url)
            
    def test_section(self):
        self.assertTrue(False)
     
if __name__ == "__main__":
    unittest.main()