from transformers import pipeline
import os
import urllib.request
from llama_cpp import Llama
import sys

class Model:
    def __init__(self, url: str = "None/None") -> None:
        self.score = [0, 0]
        self.model = None
        self.name: str = url.split("/")[-1]

    def generate_text(self, prompt):
        return prompt
    
    def __str__(self) -> str:
        return self.name

class ModelLlama(Model):
    def __init__(self,
                 url: str = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                 model_folder_path: str = 'models/',
                 context_length: int = 512) -> None:
        super().__init__()
        self.name: str = url.split("/")[-1]
        self.model_path: str = self.download_file(url, model_folder_path, self.name)
        self.model: Llama = Llama(
            model_path=self.model_path,
            n_ctx=context_length,
            n_gpu_layers=-1
        )

    @staticmethod
    def download_file(url, folder_name, file_name):
        # Dowloading GGUF model from HuggingFace, checks if the file already exists before downloading
        path = folder_name + file_name
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        if not os.path.isfile(path):
            print("Downloading model...")
            urllib.request.urlretrieve(url, path)
            print("File downloaded successfully.")
        else:
            print("File already exists.")
        return path
    
    def get_llm(self, context_length = 512, gpu_layers = 9999, cpu_threads=None):
        # Creates a Llama object
        llm = Llama(
            model_path=self.model_path,
            n_ctx=context_length, # context length to feed the model, the larger context length significantly increases time cost
            n_threads=cpu_threads, # maximum number of cpu threads to use
            n_gpu_layers=gpu_layers, # gpu layers to use if acceleration is available
        )
        return llm

    def generate_text(self, prompt, max_tokens=2048, temperature=0.1, top_p=0.5, echo=False, stop=["#", "<|im_end|>"]):
        # Generates text from the prompt provided
        prompt = "[INST] " + prompt + " [/INST]"
        output = self.model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            echo=echo,
            stop=stop,
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
        self.model = pipeline(task="table-question-answering", model=url)
        self.name = url

class ModelTapax(Model):
    def __init__(self, url: str = "microsoft/tapex-base-finetuned-wtq") -> None:
        super().__init__(url)
        self.model = pipeline(task="table-question-answering", model=url)
        self.name = url

class ModelTranslate(Model):
    def __init__(self, url: str = "") -> None:
        super().__init__(url)
        self.pipe_en_hu = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-en-hu")
        self.pipe_hu_en = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-hu-en")

    def translate_sentence(self, sentence: str, target: str = "hu"):
        if target == "hu":
            return self.pipe_en_hu(sentence)[0]['translation_text']
        return self.pipe_hu_en(sentence)[0]['translation_text']


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
    
if __name__ == "__main__":
    print(ModelLlama().generate_text("How many planets are there in our Solar System?"))
