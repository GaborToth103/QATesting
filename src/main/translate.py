# pip install transformers
# pip install torch torchvision torchaudio
# pip install sentencepiece
from transformers import pipeline
import torch

from load_database import MyDatabase


pipe_en_hu = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-en-hu")
pipe_hu_en = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-hu-en")


def write_questions(questions: list, path = 'data/questions_hu.txt'):
    with open(path, 'r') as outfile:
        outfile.write('\n'.join(str(i) for i in questions))

def read_questions(path = 'data/questions_hu.txt') -> list[str]:
    with open(path, "r") as my_file: 
        data = my_file.read() 
        data_into_list = data.split("\n") 
    return data_into_list 

def translate_sentence(sentence: str, from_en: bool = True):
    if from_en:
        return pipe_en_hu(sentence)[0]['translation_text']
    return pipe_hu_en(sentence)[0]['translation_text']

if __name__ == "__main__":
    questions: list[str] = read_questions()
    mydatabase: MyDatabase = MyDatabase()
    for index, row in enumerate(mydatabase.rows):
        if index >= 150:
            break
        try:
            table, question, truth = mydatabase.get_stuff(row)
            print(question, questions[index])
        except Exception as e:
            print(e)
            continue


