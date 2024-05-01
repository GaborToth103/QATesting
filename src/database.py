import pandas as pd
import sqlite3
import os

class Database:
    def __init__(self, path: str = 'data/database.db', parquet_path: str = 'data/wikitablequestions:test.parquet') -> None:
        self.name = parquet_path.split("/")[-1]
        df = pd.read_parquet(parquet_path)
        rows = []
        for index, row in df.iterrows():
            rows.append(row)
        self.rows: list[pd.Series] = rows

    def get_stuff(self, row: pd.Series):
        # returns table, question and answers
        row_list = row['table']['rows'].tolist()
        table = pd.DataFrame(row_list, columns=row['table']['header'])
        return table, row['question'], row['answers'][0]

    def fill_database(self, table: pd.DataFrame) -> str | None:
        # makes an SQL table based on the pandas table
        os.remove(self.path)
        conn = sqlite3.connect(self.path)
        try:
            table.rename(columns={'%': 'Percentage'}, inplace=True)
            table.rename(columns={'': 'Empty'}, inplace=True)
            table_name = 'table_name'
            table.to_sql(table_name, conn, if_exists='replace', index=False)
        except sqlite3.OperationalError as error:
            conn.close()
            raise error
        conn.commit()
        conn.close()
        return table_name

    def check_sql_answer(self, llm_answer, true_answer):
        connection = sqlite3.connect(self.path)
        try:
            cursor = connection.cursor()
            result = cursor.execute(llm_answer)
        except Exception as e:
            connection.close()
            return False
        connection.close()
        return result.fetchone() == true_answer


if __name__ == "__main__":
    mydatabase = Database()
    for index, row in enumerate(mydatabase.rows):
        table, b, c = mydatabase.get_stuff(row)
        mydatabase.fill_database(table)
