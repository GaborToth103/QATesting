from ctransformers import AutoModelForCausalLM


def stuff(token_number: int = 256, penalty: float = 1.1, temperature: float = 0.1):
    config = {'max_new_tokens': token_number, 'repetition_penalty': penalty, 'temperature': temperature, 'stream': True}
    llm = AutoModelForCausalLM.from_pretrained('TheBloke/Llama-2-7B-chat-GGML',
                                            model_type="llama",
                                            gpu_layers=110,
                                            local_files_only=True,
                                            **config
                                            )
    return llm
    
llm = None
if not llm:
    llm = stuff(64, 1.1, 0.1)


def format_answer(unformatted_answer: str):
    formatted_answer = unformatted_answer.lower().strip()
    if formatted_answer[-1] == '.':
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
    question = "Here is an unordered list of times of the day. I want you to order these in chronological order: '''afternoon, evening, night, morning, midday'''. Don't explain, just list them in order."
    answer = answer_question(question)
    print(answer)
    answer = execute_steam(question)
    print(answer)
