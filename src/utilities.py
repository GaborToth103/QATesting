import os
import sys
from enum import Enum
import time
import subprocess
import re

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

def construct_prompt(index_question: int, question: str, table: str, language_en: bool = True, prompt_type: Prompt | None = None) -> str:
    """Constructing a prompt for different LLM model types.

    Args:
        index_question (int): The question index for translating purposes.
        question (str): The question to ask (same as User Prompt) to tell the model what information to say.
        table (str): A table for User Prompt as information to help the model in str format.
        language_en (bool, optional): Whether the prompt should be english. Otherwise its hungarian. Defaults to True.
        prompt_type (Prompt | None, optional): The type of prompt as Prompt Enum type, since different model use different type of prompting. Defaults to None.

    Returns:
        str: the prompt in a string format that can be used directly for generation.
    """
    
    # This can be prompt engineered further since these prompts are entirely made up.
    if language_en:
        instruction = "You are a Question answering bot that processes table provided. Based on the table, you answer the questions without explanation. If there are multiple answers, separate them with commas."
        initiator = "The answer is: "
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

def read_data(path = 'data/questions_hu.txt') -> list[str]:
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

def get_memory_usage() -> int:
    result = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid,used_memory', '--format=csv,noheader'])
    process_memory = [line.strip().split(',') for line in result.decode('utf-8').strip().split('\n')]
    my_pid = os.getpid()
    for pid, memory in process_memory:
        return int(memory.split()[0])
        if pid == my_pid:
            pass
    return 0

def clean_string(input_string: str) -> list[str]:
    cleaned_list: list[str] = list()
    if input_string:
        cleaned_string = re.sub(r"[^\w\s]", "", input_string)
        cleaned_string = cleaned_string.lower()
        cleaned_list = cleaned_string.split()
    return cleaned_list

def scoring(truth: list[str], model_answer: list[str]) -> float:
    """Scoring function to tell how the model performed on this task. The function cleans the strings and tokenizes them. If any of the truth's token is in the model_answer's token then we accept the answer.

    Args:
        truth (list[str]): The true answer from the dataset accepted as truth to compare model answer with.
        model_answer (list[str]): The model answer that needs to be analyzed.

    Returns:
        bool: the result whether the model_answer is accepted based on the truth.
    """
    result: int = 0.0
    cleaned_truth = []
    for truth_chunk in truth:
        cleaned_truth.append(clean_string(truth_chunk))
    cleaned_answer = []
    for answer_chunk in model_answer:
        cleaned_answer.append(clean_string(answer_chunk))
    
    for answer in cleaned_answer:
        if answer in cleaned_truth:
            result += 1
    return float(result)/float(len(truth))


translated_questions: list[str] = read_data()
translated_answers: list[str] = read_data("data/answers_hu.txt")
