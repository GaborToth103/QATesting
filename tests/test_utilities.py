import sys
import os
sys.path.append(f"{os.getcwd()}/src")
import unittest
from utilities import clean_string

class TestCleanString(unittest.TestCase):

    def test_clean_string(self):
        input_list = [
            (None, []),
            ("hello", ["hello"]),
            ("aprócska kalapocska benne csacska macska mocska", ["aprócska", "kalapocska", "benne", "csacska", "macska", "mocska"]),
            ("ez.egy.nagyon.fura.string", ["ezegynagyonfurastring"]),
        ]
        for raw_string, expected_string in input_list:
            self.assertEqual(clean_string(raw_string), expected_string)

if __name__ == '__main__':
    unittest.main()
