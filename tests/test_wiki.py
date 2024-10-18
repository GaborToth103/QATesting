import pandas as pd
import re
import sys
import os
sys.path.append(f"{os.getcwd()}/src")
import unittest
from WikipediaYoinker import WikiYoinker

class TestWikiYoinker(unittest.TestCase):

    def yoink_page(self):
        """TODO check english, hungarian and """
        tables, texts = WikiYoinker.yoink_page()
        self.assertEqual(False, False)
        
if __name__ == "__main__":
    unittest.main()