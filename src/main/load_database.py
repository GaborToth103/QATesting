import pandas as pd
import json
import numpy as np


def extract(path_to_parquet):
    # Read a Parquet file
    df = pd.read_parquet(path_to_parquet)
    # Now you can work with the DataFrame 'df'
    rows = []
    for index, row in df.iterrows():
        rows.append(row)
    print("table extracted, extracted row count: ", len(rows))
    return rows

def get_stuff(row):
    # returns table, question and answers
    row_list = row['table']['rows'].tolist()
    table = pd.DataFrame(row_list, columns=row['table']['header'])
    return table, row['question'], row['answers'][0]

def get_question_column_prompt(row, has_example_rows: bool = False) -> str:
    # Extract the question and the column list in string and make an LLM prompt
    column_list = str(row['table']['header'])
    question = row['question']
    statement = " Generate an SQL statement based on the table's header: "
    example_row = "" 
    if has_example_rows:
        # TODO example row insert.
        row_list = row['table']['rows'].tolist()
        example_row += str(row_list[0])
        example_row += str(row_list[1])
        example_row += str(row_list[2])
    return str(question + statement + column_list + f" your whole answer should be an SQL statement, an example rows: {example_row}\n\nThe SQL Command:\n")

if __name__ == "__main__":
    rows = extract(r"C:\Workspace\Projects\QATesting\data\0000.parquet")
    # a, b, c =get_stuff(rows[0])
    a = get_question_column_prompt(rows[0])
    print(a)
