from database import Database, pd
from utilities import *
import transformers
import torch
import re

def ask_question_transformers(df1, is_english: bool = True):    
    df = pd.DataFrame({
        'id': [],
        'utterance': [],
        'context': [],
        'targetValue': [],
    })
        
    llama = {"3.1/70": "meta-llama/Llama-3.1-70B-Instruct",
            "3.1/8": "meta-llama/Llama-3.1-8B-Instruct"}

    pipeline = transformers.pipeline(
        "text-generation",
        model=llama["3.1/70"],
        model_kwargs={"torch_dtype": torch.bfloat16,
                    "cache_dir": "/home/p_tabtg/p_tab_llm_scratch/.hfcache/hub"},
        device_map="auto",
        max_new_tokens = 128
    )
    for x in range(30):
        answer: str = construct_clean_answer(df1.to_csv(index=False))
        prompt: str = construct_question(df1.to_csv(index=False), answer, Prompt.LLAMA3, is_english)
        question = pipeline(prompt)[0]["generated_text"]
        for match in re.findall(r'"(.*?)"', question):
            if '?' in match:
                question = match
        
        
        new_row = {
            'id': f"nt-{x}",
            'utterance': question,
            'context': "table",
            'targetValue': answer,
        }
        df.loc[len(df)] = new_row
        print(f"{x}\t{new_row['targetValue']}\t{new_row['utterance']}")
    return df

def init_dataframe(is_english: bool = True) -> pd.DataFrame:
    df1 = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Erika'],
        'Age': [25, 30, 35, 40, 28],
        'Occupation': ['Chef', 'Doctor', 'Artist', 'Lawyer', 'Agent'],
        'Salary': ["$70k", "$120k", "$50k", "$90k", "$95k"]
    })
    if is_english: return df1
    df1 = pd.DataFrame({
        'Név': ['Alice', 'Bob', 'Charlie', 'David', 'Erika'],
        'Életkor': [25, 30, 35, 40, 28],
        'Foglalkozás': ['Séf', 'Orvos', 'Művész', 'Ügyvéd', 'Ügynök'],
        'Jövedelem': ["$70k", "$120k", "$50k", "$90k", "$95k"]
    })
    return df1

def ask_questions(df1, is_english: bool):

    df = pd.DataFrame({
        'id': [],
        'utterance': [],
        'context': [],
        'targetValue': [],
    })
    mymodel = ModelLlama(url="https://huggingface.co/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q8_0.gguf")
    for x in range(30):
        asd = mymodel.generate_question(df1.to_csv(index=False), is_english)

        new_row = {
            'id': f"nt-{x}",
            'utterance': asd[0],
            'context': "table",
            'targetValue': asd[1],
        }  
        df.loc[len(df)] = new_row
        print(f"{x}\t{new_row['targetValue']}\t{new_row['utterance']}")
    return df



if __name__ == "__main__":
    english: bool = True
    df1 = init_dataframe(english)
    df = ask_question_transformers(df1, english)
    df.to_csv("/home/p_tabtg/llama_project/data/questions.csv", index=False)
    mydatabase2 = Database("data/fictional.db").fill_database(df, "qa_table")

