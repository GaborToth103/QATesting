import sys
import os
sys.path.append(f"{os.getcwd()}/src")
import unittest
from openai_module import *

class TestCleanString(unittest.TestCase):
    def test_call_openai(self):
        repeat_sentence= "Ez egy teszt."
        answer: str = call_openai(f"Say: '{repeat_sentence}'")
        self.assertIn(repeat_sentence, answer)
    
    def test_question_generation(self):
        pairs = [
            ("A postást Gábornak hívják!", "Gábor"),
            ("A labda piros.", "piros"),
            ("11.2 az átlagos hőmérséklet.", "11.2")
        ]
        for sentence, answer in pairs:
            question = generate_question_from_sentence_openai(sentence, answer)
            self.assertIsNotNone(question)
            
if __name__ == '__main__':
    unittest.main()
