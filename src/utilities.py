import os
import sys
from enum import Enum
import time

class Suppressor(object):
    def __enter__(self):
        self.outnull_file = open(os.devnull, 'w')
        self.errnull_file = open(os.devnull, 'w')

        self.old_stdout_fileno_undup    = sys.stdout.fileno()
        self.old_stderr_fileno_undup    = sys.stderr.fileno()

        self.old_stdout_fileno = os.dup ( sys.stdout.fileno() )
        self.old_stderr_fileno = os.dup ( sys.stderr.fileno() )

        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr

        os.dup2 ( self.outnull_file.fileno(), self.old_stdout_fileno_undup )
        os.dup2 ( self.errnull_file.fileno(), self.old_stderr_fileno_undup )

        sys.stdout = self.outnull_file        
        sys.stderr = self.errnull_file
        return self

    def __exit__(self, *_):        
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

        os.dup2 ( self.old_stdout_fileno, self.old_stdout_fileno_undup )
        os.dup2 ( self.old_stderr_fileno, self.old_stderr_fileno_undup )

        os.close ( self.old_stdout_fileno )
        os.close ( self.old_stderr_fileno )

        self.outnull_file.close()
        self.errnull_file.close()

class Prompt(Enum):
    DEFAULT = -1
    MICROSOFT = 0
    LLAMA2HUN = 1
    LLAMA2 = 2
    LLAMA3 = 3

def construct_prompt(index_question: int, question: str, table, language_en: bool = True, prompt_type: Prompt | None = None) -> str:
    """Constructing a prompt for different LLM model types.

    Args:
        index_question (int): The question index for translating purposes.
        question (str): The question to ask (same as User Prompt) to tell the model what information to say.
        table: A table for User Prompt as information to help the model.
        language_en (bool, optional): Whether the prompt should be english. Otherwise its hungarian. Defaults to True.
        prompt_type (Prompt | None, optional): The type of prompt as Prompt Enum type, since different model use different type of prompting. Defaults to None.

    Returns:
        str: the prompt in a string format that can be used directly for generation.
    """
    
    # This can be prompt engineered further since these prompts are entirely made up.
    if language_en:
        instruction = "You are a Question answering bot that processes table provided. Based on the table, you answer the questions in a single sentence without explanation."
        initiator = "The short answer is "
    else:
        question = translated_questions[index_question]
        instruction = "Válaszolj az alábbi kérdésre a lenti táblázat alapján! Tömören válaszolj. A válasz csak egy cella tartalma legyen. Ne írj magyarázatot!"        
        initiator = "A tömör válasz tömören: "

    # This should not be modified, as it matches the training data.
    match prompt_type:
        case Prompt.MICROSOFT:
            return f"<|system|>\n{instruction}<|end|>\n<|user|>\n{table}\n\n{question}<end>\n<|assistant|>\n{initiator}"
        case Prompt.LLAMA3:
            return f"<|im_start|>system\n{instruction}<|im_end|>\n<|im_start|>user\n{table}\n\n{question}<|im_end|>\n<|im_start|>assistant\n{initiator}"
        case Prompt.LLAMA2:
            return f"[INST] <<SYS>>\n{instruction}\n<</SYS>>\n{table}\n\n{question}[/INST]\n{initiator}"
        case Prompt.LLAMA2HUN:
            return f"<|system|>\n{instruction}</s><|end|>\n<|user|>\n{table}\n\n{question}</s><end>\n<|assistant|>\n{initiator}"
        case _: 
            return f"{instruction}\n\n{table}\n\n{question}\n\n{initiator}"

def read_questions(path = 'data/questions_hu.txt') -> list[str]:
    with open(path, "r") as my_file: 
        data = my_file.read() 
        data_into_list = data.split("\n") 
    return data_into_list 

def measure_time(func):
    """Measuring time spent on function"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        return result, elapsed_time
    return wrapper

translated_questions: list[str] = read_questions()