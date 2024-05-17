import urllib.request
from llama_cpp import Llama
import os
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from database import Database
from tqdm import tqdm
from utilities import *

class Model:
    def __init__(self, url: str = "None/None") -> None:
        self.score: list[int] = list()
        self.model = None
        self.name: str = url.split("/")[-1]

    def generate_text(self, table: pd.DataFrame, question: str) -> str:
        prompt = f"{table}\n{question}\nBase model answer."
        return prompt
    
    def __str__(self) -> str:
        return self.name

class ModelLlama(Model):
    def __init__(self,
                 url: str,
                 model_folder_path: str = 'models/',
                 context_length: int = 4096, n_gpu_layers=-1, prompt_format: Prompt = Prompt.LLAMA3, lang_en: bool = True) -> None:
        super().__init__()
        self.name: str = url.split("/")[-1]
        self.model_path: str = self.download_file(url, model_folder_path, self.name)
        with Suppressor():
            self.model: Llama = Llama(
                model_path=self.model_path,
                n_ctx=9000,
                n_gpu_layers=-1,
            )
        self.prompt_format: Prompt = prompt_format
        self.lang_en: bool = lang_en

    @staticmethod
    def download_file(url: str, folder_path: str, name: str) -> str:
        """Dowloading GGUF model from HuggingFace, checks if the file already exists before downloading.

        Args:
            url (str): URL to the HuggingFace gguf file.
            folder_path (str): The relative or absolute folder path.

        Returns:
            str: The absolute local file path.
        """
        file_path = folder_path + name
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        if not os.path.isfile(file_path):
            print(f"Downloading model to {file_path} now.")
            urllib.request.urlretrieve(url, file_path)
            print(f"File downloaded successfully to {file_path}")
        return file_path

    def generate_text(self, index, table: pd.DataFrame, question: str) -> str:
        with Suppressor():
            output = self.model(
                construct_prompt(index, question, table, self.lang_en, self.prompt_format),
                max_tokens=None,
                echo=False,
                stop=["<|", "<</", "[/INST]", "[INST]", "</s>", "\n", ". "],
            )
        return output["choices"][0]["text"].strip()

    @staticmethod
    def reduce_table_size(input_table, max_size: int = 64):
        num_rows, num_cols = input_table.shape
        current_size = num_rows * num_cols + 1  # +1 for the header
        if current_size > max_size:
            rows_to_remove = int((current_size - max_size) / num_cols)
            reduced_table = input_table.iloc[:-rows_to_remove, :]
            return reduced_table
        else:
            return input_table

    @staticmethod
    def execute_steam(prompt: str):
        pass

    @staticmethod
    def initalize_model():
        pass

class ModelTapas(Model):
    def __init__(self, url: str = "google/tapas-base-finetuned-wtq") -> None:
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(url)
        self.model = AutoModelForTableQuestionAnswering.from_pretrained(url)

    def generate_text(self, table: pd.DataFrame, question: str) -> str:
        inputs = self.tokenizer(table=table, queries=[question], padding="max_length", return_tensors="pt")
        outputs = self.model(**inputs)
        predicted_answer_coordinates = self.tokenizer.convert_logits_to_predictions(inputs, outputs.logits.detach(), outputs.logits_aggregation.detach())[0][0]
        return table.iat[predicted_answer_coordinates[0]]

class ModelTapex(Model):
    def __init__(self, url: str = "microsoft/tapex-base-finetuned-wtq") -> None:
        super().__init__(url)
        self.tokenizer = AutoTokenizer.from_pretrained(url)
        self.model = BartForConditionalGeneration.from_pretrained(url)

    def generate_text(self, table, question: str):
        inputs = self.tokenizer(table=table, query=question, return_tensors="pt")
        outputs = self.model.generate(**inputs)
        return self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

class ModelTranslate(Model):
    def __init__(self, url: str = "Helsinki-NLP/opus-mt-en-hu") -> None:
        """Translator used for translating questions for the dataset"""
        torch.device('cuda:0')
        self.tokenizer = AutoTokenizer.from_pretrained(url)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(url)
        self.questions: list[str] = []
        self.database: Database = Database()
        self.answers: list[str] = []

    def translate_questions(self):
        for row in tqdm(self.database.rows):
            try:
                table, question, truth = self.database.extract_parquet(row)
                self.questions.append(self.translate(question))
            except Exception as e:
                print(e)
                continue
        self.write_list_to_file(self.questions)

    def translate_answers(self):
        for row in tqdm(self.database.rows):
            try:
                table, question, truth = self.database.extract_parquet(row)
                self.answers.append(self.translate(truth))
            except Exception as e:
                print(e)
                continue
        self.write_list_to_file(self.answers, path='data/answers_hu.txt')
    
    def translate(self, sample_text):
        batch = self.tokenizer([sample_text], return_tensors="pt")
        generated_ids = self.model.generate(**batch)
        result = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return result

    @staticmethod
    def write_list_to_file(list_of_sentences: list, path = 'data/questions_hu.txt'):
        with open(path, 'w') as outfile:
            outfile.write('\n'.join(str(i) for i in list_of_sentences))
    
    @staticmethod
    def read_questions(path = 'data/questions_hu.txt') -> list[str]:
        with open(path, "r") as my_file: 
            data = my_file.read() 
            data_into_list = data.split("\n") 
        return data_into_list 

if __name__ == "__main__":
    ModelTranslate().translate_answers()