from transformers import pipeline

unmasker = pipeline('fill-mask', model='xlm-roberta-base')

def unmask(sentence: str, word: str) -> str:
    """Given a statement with a word, where the word must be masked and we need to replace dot with questionmark at the end."""
    new_sentence = sentence.replace(word, "<mask>").replace(".", "?")
    answer = unmasker(new_sentence)
    missing_item: str = answer[0]['sequence']
    print(missing_item)
    return missing_item

if __name__ == "__main__":
    unmask("A labda zöld színű.", "zöld")
    unmask("A 2011-es népszámlálás adatok szerint a város lakossága 168048 fő volt.", "168048")
    unmask("Az éves átlagos hőmérséklet 11,2 °C.", "11,2")