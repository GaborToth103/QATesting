import urllib.request
from llama_cpp import Llama
import os
import pandas as pd
from enum import Enum, auto

def read_questions(path = 'data/questions_hu.txt') -> list[str]:
    with open(path, "r") as my_file: 
        data = my_file.read() 
        data_into_list = data.split("\n") 
    return data_into_list 

questions: list[str] = read_questions()

class Prompt(Enum):
    MICROSOFT = 0
    LLAMA2HUN = 1
    LLAMA2 = 2
    LLAMA3 = 3

def construct_prompt(index_question: int, question: str, table: pd.DataFrame = pd.DataFrame(), language_en: bool = True, prompt_type: Prompt | None = None) -> str:
    """Constructing a prompt for different LLM model types.

    Args:
        index_question (int): The question index for translating purposes.
        question (str): The question to ask (same as User Prompt) to tell the model what information to say.
        table (pd.DataFrame, optional): A table (dataframe) for User Prompt as information to help the model. Defaults to pd.DataFrame().
        language_en (bool, optional): Whether the prompt should be english. Otherwise its hungarian. Defaults to True.
        prompt_type (Prompt | None, optional): The type of prompt as Prompt Enum type, since different model use different type of prompting. Defaults to None.

    Returns:
        str: the prompt in a string format that can be used directly for generation.
    """
    
    # This can be prompt engineered further since this is entirely made up.
    if language_en:
        instruction = "You are a Question answering bot that processes table provided. Based on the table, answer the questions briefly!"
    else:
        instruction = "Válaszolj az alábbi kérdésre a lenti táblázat alapján! Tömören válaszolj. A válasz csak egy cella tartalma legyen. Ne írj magyarázatot!"        
        question = questions[index_question]

    # This should not be modified, as it matches the training data.
    match prompt_type:
        case Prompt.MICROSOFT:
            return f"<|system|>\n{instruction}<|end|>\n<|user|>\n{table}\n\n{question}<end>\n<|assistant|>\n"
        case Prompt.LLAMA3:
            return f"<|im_start|>system\n{instruction}<|im_end|>\n<|im_start|>user\n{table}\n\n{question}<|im_end|>\n<|im_start|>assistant\n"
        case Prompt.LLAMA2:
            return f"[INST] <<SYS>>\n{instruction}\n<</SYS>>\n{table}\n\n{question}[/INST]"
        case Prompt.LLAMA2HUN:
            return f"<|system|>\n{instruction}</s><|end|>\n<|user|>\n{table}\n\n{question}</s><end>\n<|assistant|>\n"
        case _: 
            return f"{instruction}\n\n{table}\n\n{question}\n\nThe answer: "

class Tranlator:
    def __init__(self) -> None:
        from transformers import pipeline
        import torch
        self.pipe_en_hu = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-en-hu")
        self.pipe_hu_en = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-hu-en")

    def translate_sentence(self, sentence: str, from_en: bool = True):
        if from_en:
            return self.pipe_en_hu(sentence)[0]['translation_text']
        return self.pipe_hu_en(sentence)[0]['translation_text']


class Model:
    def __init__(self, url: str = "None/None") -> None:
        self.score = [0, 0]
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
        self.model: Llama = Llama(
            model_path=self.model_path,
            n_ctx=context_length,
            n_gpu_layers=n_gpu_layers,
            n_threads=8,
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
        output = self.model(
            construct_prompt(index, question, table, self.lang_en, self.prompt_format),
            max_tokens=4096,
            echo=False,
            stop=["<|", "<</", "[/INST]", "[INST]", "</s>"],
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
    def __init__(self, url: str = "Helsinki-NLP/opus-mt-en-hu", url2: str = "Helsinki-NLP/opus-mt-hu_en") -> None:
        super().__init__(url)
        self.tokenizer = AutoTokenizer.from_pretrained(url, cache_dir="models")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(url, cache_dir="models")
        self.tokenizer2 = AutoTokenizer.from_pretrained(url2)
        self.model2 = AutoModelForSeq2SeqLM.from_pretrained(url2)

        model_dir="./models/models--Helsinki-NLP--opus-mt-en-hu"
        _ = self.model.save_pretrained(model_dir)
        _ = self.tokenizer.save_pretrained(model_dir)

        model_dir2="./models/models--Helsinki-NLP--opus-mt-hu-en"
        _ = self.model2.save_pretrained(model_dir2)
        _ = self.tokenizer2.save_pretrained(model_dir2)

        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
        self.tokenizer2 = AutoTokenizer.from_pretrained(model_dir2)
        self.model2 = AutoModelForSeq2SeqLM.from_pretrained(model_dir2)

    def translate_sentence(self, sentence: str, target: str = "hu"):
        tokenizer = self.tokenizer
        model = self.model
        if target == "en":
            tokenizer = self.tokenizer2
            model = self.model2
        inputs= tokenizer([sentence], return_tensors="pt")
        generated_ids = model.generate(**inputs)
        return tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    def back_and_forth_translate(self, question: str) -> str:
        """ Translating an english text to hungarian and back to english to simulate hungarian text being solved by these english only models.

        Args:
            question (str): The question to translate back and forth.

        Returns:
            str: the Sretranslated question.
        """
        question = self.translate_sentence(question, "hu")
        question = self.translate_sentence(question, "en")
        return question
