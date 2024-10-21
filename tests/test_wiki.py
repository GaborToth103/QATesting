import pandas as pd
import re
import sys
import os
sys.path.append(f"{os.getcwd()}/src")
import unittest
from WikipediaYoinker import WikiYoinker

class TestWikiYoinker(unittest.TestCase):        
    def test_transform_statement_to_question(self):
        wikiyoinker = WikiYoinker()
        
        # TODO more testcases
        pairs = [
            ("Őt Gábornak hívják!", "Gábornak"),
            ("A labda piros.", "piros")
        ]
        for pair in pairs:
            question = wikiyoinker.transform_statement_to_question(*pair)
            print(question)
            self.assertEqual(type(question), str)
            self.assertEqual(question[-1], "?")
            self.assertNotIn("<mask>", question)
        
        
        
        
if __name__ == "__main__":
    unittest.main()