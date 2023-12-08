import pandas as pd
import json
import numpy as np


def extract():
    # Read a Parquet file
    df = pd.read_parquet('D:\\project\\egyetem\\QuestionAnswering\\0000.parquet')
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

if __name__ == "__main__":
    rows = extract()
    a, b, c =get_stuff(rows[0])
    print(a)
    print(b)
    print(c)