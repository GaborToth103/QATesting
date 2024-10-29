import os
from openai import OpenAI

def call_openai(user_input: str, model: str = "gpt-3.5-turbo") -> str:
    """Calls OpenAI API to get answer with a single chat completion input.

    Args:
        user_input (str): The user input in string format.
        model (str, optional): The selected model to call with API. Defaults to "gpt-3.5-turbo".

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
                "content": user_input,
            }
        ],
        model=model,
    )

    return chat_completion.choices[0].message.content
    
if __name__ == "__main__":
    print(call_openai("Say this is a test"))
