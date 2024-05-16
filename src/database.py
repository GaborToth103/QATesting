import pandas as pd
import sqlite3
import os

class Database:
    def __init__(self, path: str = 'data/database.db', parquet_path: str = 'data/wikitablequestions:test.parquet') -> None:
        self.name = parquet_path.split("/")[-1]
        df = pd.read_parquet(parquet_path)
        rows = []
        for index, row in df.iterrows():
            duplicate = len(df.columns) != len(df.columns.str.replace('.1$', '').drop_duplicates())
            if not duplicate:
                rows.append(row)
        self.rows: list[pd.Series] = rows
        self.path = path

    def extract_parquet(self, row: pd.Series) -> tuple[pd.DataFrame, str, str]:
        """Extract Parquet Data

        Args:
            row (pd.Series): For a row of the parquet data extract the table, the question and the answer. 

        Returns:
            tuple[pd.DataFrame, str, str]: Returns the Table, Question, Answer data respectively.
        """
        row_list = row['table']['rows'].tolist()
        table = pd.DataFrame(row_list, columns=row['table']['header'])        
        return table, row['question'], " ".join(row['answers']) 

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

    def parquet_table_to_csv(self):
        for row in self.rows:
            table, b, c = self.extract_parquet(row)
            try:
                self.fill_database(table)
            except Exception as e:
                table.to_csv('data/table.csv')
                print(e)
                print(table["Terminals"])
                exit()

if __name__ == "__main__":    
    Database().parquet_table_to_csv()