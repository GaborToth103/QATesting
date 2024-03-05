from ctransformers import AutoModelForCausalLM


def stuff(token_number: int = 256, penalty: float = 1.1, temperature: float = 0.1):
    models = ['TheBloke/Llama-2-13B-chat-GGUF', 'TheBloke/Spicyboros-13B-2.2-GGUF', 'TheBloke/Spicyboros-7B-2.2-GGUF', 'TheBloke/MythoMax-L2-13B-GGUF', 'TheBloke/Llama-2-7B-chat-GGUF']
    config = {'max_new_tokens': token_number, 'repetition_penalty': penalty, 'temperature': temperature, 'stream': True}
    llm = AutoModelForCausalLM.from_pretrained(models[3],
                                            model_type="llama",
                                            gpu_layers=130,
                                            local_files_only=True,
                                            **config
                                            )
    return llm
    
llm = None
if not llm:
    llm = stuff(256, 1.1, 0.1)


def format_answer(unformatted_answer: str):
    formatted_answer = unformatted_answer.lower().strip()
    if formatted_answer and formatted_answer[-1] == '.':
        formatted_answer = formatted_answer[:-1]
    return str(formatted_answer)

def answer_question(question: str):
    result = llm(question, stream=False)
    return result

def execute_steam(prompt: str):
    tokens = llm.tokenize(prompt)
    answer = ""
    num = 0
    for token in llm.generate(tokens):
        num += 1
        answer += str(llm.detokenize(token))
        if num > 16:
            break
    return format_answer(answer)

def reduce_table_size(input_table, max_size: int = 64):
    num_rows, num_cols = input_table.shape
    current_size = num_rows * num_cols + 1  # +1 for the header
    if current_size > max_size:
        rows_to_remove = int((current_size - max_size) / num_cols)
        reduced_table = input_table.iloc[:-rows_to_remove, :]
        return reduced_table
    else:
        return input_table

if __name__ == "__main__":
    question = "User: There is a table with rows: id, name, birthday, location. Give me an SQL command that returns with the name of the oldest person.\n\nBot: Sure! The answer is:\n"
    answer = answer_question(question)
    print(answer)
    answer = execute_steam(question)
    print(answer)
