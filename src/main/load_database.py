import pandas as pd
import json
import numpy as np
import sqlite3
import os


def extract(path):
    # Read a Parquet file
    df = pd.read_parquet(path)
    # Now you can work with the DataFrame 'df'
    rows = []
    for index, row in df.iterrows():
        rows.append(row)
    print("table extracted, extracted row count: ", len(rows))
    return rows

def get_stuff(row: pd.Series):
    # returns table, question and answers
    row_list = row['table']['rows'].tolist()
    table = pd.DataFrame(row_list, columns=row['table']['header'])
    return table, row['question'], row['answers'][0]

def fill_database(table: pd.DataFrame) -> str | None:
    # makes an SQL table based on the pandas table
    conn = sqlite3.connect(db_path)
    table.rename(columns={'%': 'Percentage'}, inplace=True)
    table.rename(columns={'': 'Empty'}, inplace=True)
    table_name = 'table_name'
    try:
        table.to_sql(table_name, conn, if_exists='replace', index=False)
    except sqlite3.OperationalError as message:
        print(message)
        return None
    conn.commit()
    conn.close()
    return table_name

if __name__ == "__main__":
    db_path = 'data/database.db'
    os.remove(db_path)
    rows = extract('data/0000.parquet')
    for index, row in enumerate(rows):
        table, b, c =get_stuff(row)
        fill_database(table)
