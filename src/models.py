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

    def generate_text(self, table: str, question: str) -> str:
        """Generating text based on the question and the table.

        Args:
            table (str): The table as an already formatted string.
            question (str): The question as a string.

        Returns:
            str: The model answer, answers must be separated by a comma.
        """
        prompt = f"{table}\n{question}\nBase model answer."
        return prompt
    
    def generate_question(self, table: str) -> tuple[str, str]:
        """Generates a question from the input table and it's answer part.

        Args:
            table (str): datatable in an str format.

        Returns:
            tuple[str, str]: The question and it's answer.
        """
        question = "What does the table contain?"
        answer = table
        return question, answer
    
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

    def generate_text(self, index: int, table: str, question: str) -> str:
        with Suppressor():
            output = self.model(
                construct_prompt(index, question, table, self.lang_en, self.prompt_format),
                max_tokens=None,
                echo=False,
                stop=stopping_tokens,
            )
        return output["choices"][0]["text"].strip()
    
    def generate_question(self, table: str) -> tuple[str, str]:
        with Suppressor():
            output = self.model(
                construct_answer(table, self.prompt_format),
                max_tokens=None,
                echo=False,
                stop=stopping_tokens,
            )
        answer: str = output["choices"][0]["text"].strip()
        with Suppressor():
            output = self.model(
                construct_question(table, answer, self.prompt_format),
                max_tokens=None,
                echo=False,
                stop=stopping_tokens,
            )
        question: str = output["choices"][0]["text"].strip()
        return question, answer

    @staticmethod
    def reduce_table_size(input_table: pd.DataFrame, max_size: int = 64):
        """Reducing table size if it's too large 

        Args:
            input_table (pandas.Dataframe): The large table
            max_size (int, optional): Max token size of the table. Defaults to 64.

        Returns:
            pandas.Dataframe: reduced dataframe
        """
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
        raise NotImplementedError

    @staticmethod
    def initalize_model():
        raise NotImplementedError

class ModelTapas(Model):
    def __init__(self, url: str = "google/tapas-base-finetuned-wtq") -> None:
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(url)
        self.model = AutoModelForTableQuestionAnswering.from_pretrained(url)

    def generate_text(self, table: str, question: str) -> str:
        inputs = self.tokenizer(table=table, queries=[question], padding="max_length", return_tensors="pt")
        outputs = self.model(**inputs)
        predicted_answer_coordinates = self.tokenizer.convert_logits_to_predictions(inputs, outputs.logits.detach(), outputs.logits_aggregation.detach())[0][0]
        return table.iat[predicted_answer_coordinates[0]]

class ModelTapex(Model):
    def __init__(self, url: str = "microsoft/tapex-base-finetuned-wtq") -> None:
        super().__init__(url)
        self.tokenizer = AutoTokenizer.from_pretrained(url)
        self.model = BartForConditionalGeneration.from_pretrained(url)

    def generate_text(self, table: str, question: str):
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
        """Translating questions and writing to the questions file"""
        for row in tqdm(self.database.rows):
            try:
                table, question, truth = self.database.extract_parquet(row)
                self.questions.append(self.translate(question))
            except Exception as e:
                print(e)
                continue
        self.write_list_to_file(self.questions)

    def translate_answers(self):
        """Translating answers and writing to the answers file"""
        for row in tqdm(self.database.rows):
            try:
                table, question, truth = self.database.extract_parquet(row)
                self.answers.append(self.translate(truth))
            except Exception as e:
                print(e)
                continue
        self.write_list_to_file(self.answers, path='data/answers_hu.txt')
    
    def translate(self, sample_text: str) -> str:
        """Translating sample_text.

        Args:
            sample_text (str): The text to translate.

        Returns:
            str: the translated result
        """
        batch = self.tokenizer([sample_text], return_tensors="pt")
        generated_ids = self.model.generate(**batch)
        result = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return result

    @staticmethod
    def write_list_to_file(list_of_sentences: list, path = 'data/questions_hu.txt'):
        """ Take a list of sentences and a path, it writes the list to the exact file

        Args:
            list_of_sentences (list): The list of sentences in a list.
            path (str, optional): The path to the target file. Defaults to 'data/questions_hu.txt'.
        """
        with open(path, 'w') as outfile:
            outfile.write('\n'.join(str(i) for i in list_of_sentences))
    
    @staticmethod
    def read_questions(path = 'data/questions_hu.txt') -> list[str]:
        """Read the questions from the path and put these data to a list of strings.

        Args:
            path (str, optional): The relative path to the questions file. Defaults to 'data/questions_hu.txt'.

        Returns:
            list[str]: List of questions.
        """
        with open(path, "r") as my_file: 
            data = my_file.read() 
            data_into_list = data.split("\n") 
        return data_into_list 

if __name__ == "__main__":
    # ModelTranslate().translate_answers()
    mymodel = ModelLlama(url="https://huggingface.co/lmstudio-community/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q3_K_L.gguf")

    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
        'Age': [25, 30, 35, 40, 28],
        'Occupation': ['Engineer', 'Doctor', 'Artist', 'Lawyer', 'Scientist'],
        'Salary': [70000, 120000, 50000, 90000, 95000]
    }

    df1 = pd.DataFrame(data)

        
    
    qa = {
        'id': [],
        'utterance': [],
        'context': [],
        'targetValue': [],
    }  
    df = pd.DataFrame(qa)

    for x in range(0):
        asd = mymodel.generate_question(df1.to_csv(index=False))

        new_row = {
            'id': f"nt-{x}",
            'utterance': asd[0],
            'context': "table",
            'targetValue': asd[1],
        }  
        df.loc[len(df)] = new_row
        print(new_row)
    
    mydatabase2 = Database("data/fictional.db")    
    mydatabase2.fill_database(df, "qa_table") # TODO goal
    
    generated_text = mymodel.generate_text(0, df1, "Who is an Artist? Answer with a content of single cell?")
    print(generated_text)
