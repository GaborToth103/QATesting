import sys
import os
sys.path.append(f"{os.getcwd()}/src")
import unittest
import pandas as pd
from database import Database

class TestDatabase(unittest.TestCase):
    test_database_path = "data/test_database.db"
    wtq_path = '/home/gabortoth/Dokumentumok/Data/WikiTableQuestions'
    
    def test_creating_fictional_database(self):
        # make sure the function takes a table, a section_tableno name, and a list of qa tuples.
        old_table = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
            'Age': [25, 30, 35, 40, 28],
            'Occupation': ['Engineer', 'Doctor', 'Artist', 'Lawyer', 'Scientist'],
            'Salary': [70000, 120000, 50000, 90000, 95000]
        })        
        qa = [('How old is alice?', '25'), ('What is the occupation of Bob?', 'Doctor'), ('Who earns 50000?','Charlie')]
        section_table_id = 'People_0'
        
        # Execution
        db = Database(self.test_database_path)    
        db.generate_questions_table(section_table_id, old_table, qa, 'replace')

        # Test
        for x in range(db.get_database_info()):
            new_table, question, answers = db.get_question_with_table(x)
            self.assertEqual(new_table['Name'][0], old_table['Name'][0])
            self.assertEqual(question, qa[x][0])
            self.assertEqual(answers, [qa[x][1]])

    def test_uploading_wtq(self):
        mydatabase = Database(self.test_database_path)
        mydatabase.wtq_collector(self.wtq_path)
        self.assertTrue(mydatabase.get_question_with_table(0))

    def test_create_qa_table(self):
        # TODO we need a qa table generation method
        qa = {
            'id': ['nt-0'],
            'utterance': ['asd'],
            'context': ['table'],
            'targetValue': ['0'],
        }    
        qa_table = pd.DataFrame(qa)
        raise NotImplementedError()

if __name__ == '__main__':
    unittest.main()
