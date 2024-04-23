from transformers import AutoTokenizer, AutoModelForTableQuestionAnswering, BartForConditionalGeneration, AutoModelForSeq2SeqLM, AutoModelForCausalLM
import urllib.request
from llama_cpp import Llama
import os
import pandas as pd
import torch

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

class ModelLlama3(Model):
    def __init__(self, url: str = "None/None") -> None:
        super().__init__(url)
        model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )

        messages = [
            {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
            {"role": "user", "content": "Who are you?"},
        ]

        input_ids = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)

        terminators = [
            tokenizer.eos_token_id,
            tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        outputs = model.generate(
            input_ids,
            max_new_tokens=256,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
        )
        response = outputs[0][input_ids.shape[-1]:]
        print(tokenizer.decode(response, skip_special_tokens=True))


class ModelLlama(Model):
    def __init__(self,
                 url: str = "https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf",
                 model_folder_path: str = 'models/',
                 context_length: int = 8192) -> None:
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

    def generate_text(self, table: pd.DataFrame, question: str) -> str:
        prompt = f"{table}\n{question}\n In one word, the answer is:"
        output = self.model(
            prompt,
            max_tokens=2048,
            temperature=0.1,
            top_p=0.5,
            echo=False,
            stop=["#", "<|im_end|>", "\n", "."],
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
        return self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

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
    ModelLlama3()
    exit()
    print(
        ModelLlama().generate_text(
            pd.DataFrame(),
            "How many planets are there in our Solar System?"
        )
    )
