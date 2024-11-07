import sys
import os
sys.path.append(f"{os.getcwd()}/src")
import pandas as pd
import re
import unittest
from WikipediaYoinker import WikiYoinker, Section
from database import Database
from mylogger import MyLogger
from report import Report

class TestWikiYoinker(unittest.TestCase):        
    data_path = "data/generated_hu.db"
    starting_page = "Szeged"
    log_path = 'data/wiki.log'
    page_count = 1
    
    database = Database(data_path)
    database.empty_database()
    logger: MyLogger = MyLogger(log_path=log_path, result_path=log_path)    
    wikiyoinker = WikiYoinker(starting_page_name=starting_page, use_openai=False, strict=True, logger=logger)
    
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

    def test_convert_url_to_section_data(self):
        self.assertTrue(False)
        
    def test_main(self):
        self.wikiyoinker.use_openai = True
        for x in range(self.page_count):
            req = self.wikiyoinker.get_next_page()
            sections = self.wikiyoinker.convert_url_to_section_data(req.url)
            self.wikiyoinker.process_sections(sections, self.logger, self.database, req.url)
        Report().create_report_from_db()
        self.assertTrue(True)
        
    def test_duplicate(self):
        self.assertTrue(1)

if __name__ == "__main__":
    unittest.main()