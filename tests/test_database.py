import sys
import os
sys.path.append(f"{os.getcwd()}/src")
import unittest
import pandas as pd
from database import Database

class TestDatabase(unittest.TestCase):
    def test_creating_fictional_database(self):
        data = {
            'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
            'Age': [25, 30, 35, 40, 28],
            'Occupation': ['Engineer', 'Doctor', 'Artist', 'Lawyer', 'Scientist'],
            'Salary': [70000, 120000, 50000, 90000, 95000]
        }
        df = pd.DataFrame(data)
        qa = {
            'id': ['nt-0'],
            'utterance': ['asd'],
            'context': ['table'],
            'targetValue': ['0'],
        }    
        df2 = pd.DataFrame(qa)

        # To fill fictional and get something:
        mydatabase2 = Database("data/test_database.db")    
        mydatabase2.generate_questions_table(df, df2)
        self.assertTrue(mydatabase2.get_question_with_table(0))

    def test_uploading_wtq(self):
        mydatabase = Database('data/test_database.db')
        mydatabase.wtq_collector('/home/gabortoth/Dokumentumok/Data/WikiTableQuestions')
        self.assertTrue(mydatabase.get_question_with_table(0))

if __name__ == '__main__':
    unittest.main()
