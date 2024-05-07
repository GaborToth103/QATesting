from src.utilities import clean_string

def test_clean_string():
    input_list: list[tuple] = [
        (None, []),
        ("hello", ["hello"]),
        ("aprócska kalapocska benne csacska macska mocska", ["aprócska","kalapocska","benne","csacska","macska","mocska"]),
        ("ez.egy.nagyon.fura.string", ["ezegynagyonfurastring"]),
    ]
    for raw_string, expected_string in input_list:
        assert clean_string(raw_string) == expected_string
