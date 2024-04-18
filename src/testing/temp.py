import load_database
import llama2

def example_procedure() -> str:
    # returns an SQL command to answer the question
    # TODO give example row(s) as format so the LLM knows what to do
    # TODO prompt engineering
    # TODO better model
    # TODO try python code maybe?
    rows = load_database.extract(path_to_parquet='data/0000.parquet')
    selected_row = rows[0]
    a, b, c = load_database.get_stuff(selected_row)
    print(a)
    print(b)
    prompt = load_database.get_question_column_prompt(selected_row, has_example_rows=True)
    print(prompt)
    answer: str = llama2.answer_question(prompt)
    command = answer.split(";")[0].strip()
    return command

if __name__ == "__main__":
    print(example_procedure())
