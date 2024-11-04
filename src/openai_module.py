import os
from openai import OpenAI

def call_openai(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """Calls OpenAI API to get answer with a single chat completion input.

    Args:
        prompt (str): The user input in string format.
        model (str, optional): The selected model to call with API. Defaults to "gpt-3.5-turbo".

    Raises:
        TypeError: The return value type must be string.

    Returns:
        str: The answer in string format.
    """
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
    )
    answer = chat_completion.choices[0].message.content
    if type(answer) != str:
        raise TypeError(f"The answer is not a string. The answer:\n{answer}") 
    return answer
        

def generate_question_from_sentence(sentence: str, answer: str) -> str:
    """Generates a question from a sentence and an answer. The function masks the answer in the sentence and makes it 

    Args:
        sentence (str): The sentence to transform into a
        answer (str): The answer so the question must  

    Raises:
        ValueError: It must return a complete question string.

    Returns:
        str: the question string.
    """
    prompt = f"Mondat:{sentence}\nVálasz:{answer}\nAlakítsd át a mondatot úgy, hogy vedd ki belőle a választ és tedd fel úgy kérdésként, hogy arra a válasz a Válasz legyen! Csak a kérdést írd ki! Ügyelj arra, hogy a válasz ne maradjon benne a kérdésben!"
    question = call_openai(prompt)
    if not question.endswith("?"):
        raise ValueError(f"question must be a question. The output looks like this:\n{question}")
    return question