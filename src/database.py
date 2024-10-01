import pandas as pd
import sqlite3
import os

class Database:
    def __init__(self, path: str = 'data/database.db') -> None:
        self.path = path

    def dataframe_from_parquet(self, parquet_path):
        df = pd.read_parquet(parquet_path)
        rows = []
        for index, row in df.iterrows():
            duplicate = len(df.columns) != len(df.columns.str.replace('.1$', '').drop_duplicates())
            if not duplicate:
                rows.append(row)
        return rows
    
    def wtq_collector(self, wtq_path: str) -> tuple[list, list]:
        """Filling the local sqlite3 database with WTQ tables and the QA Table to answer the questions""" 
        def collect_tables(directory: str) -> list[str]:
            # Walk through the directory and all subdirectories
            csv_files = []            
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".tsv"):
                        csv_files.append(os.path.join(root, file))
            
            return csv_files
        
        def upload_tables_to_database(tables: list[str]):
            for table in tables:
                try:
                    df = pd.read_csv(table, delimiter="\t")
                except Exception as e:
                    df = pd.read_csv(table.replace(".tsv",".csv"))
                finally:
                    df_name = ("csv/" + table.split("/")[-2] + "/" + table.split("/")[-1]).replace(".tsv", ".csv")
                    self.fill_database(df, df_name)

        def upload_questiontables_to_database(directory: str):
            df = pd.read_csv(directory, delimiter="\t")
            return self.fill_database(df, "qa_table")            

        csv_files = collect_tables(f'{wtq_path}/csv')
        upload_tables_to_database(tables=csv_files)
        upload_questiontables_to_database(f'{wtq_path}/data/training.tsv')

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

    def fill_database(self, table: pd.DataFrame, table_name: str) -> str | None:
        # makes an SQL table based on the pandas table
        # os.remove(self.path)
        conn = sqlite3.connect(self.path)
        try:
            table.rename(columns={'%': 'Percentage'}, inplace=True)
            table.rename(columns={'': 'Empty'}, inplace=True)
            table.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.commit()
        except pd.errors.DatabaseError as error:
            print(table_name)
            raise error
        finally:
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

    def get_question_with_table(self, id: str) -> tuple[pd.DataFrame, str, list[str]]:
        """from the id, get the table, the question and the answer as return values""" 
        connection = sqlite3.connect(self.path)
        try:
            cursor = connection.cursor()
            query = f"SELECT utterance, context, targetValue FROM qa_table where id = 'nt-{id}'"
            cursor.execute(query)
            question, data_path, answers = cursor.fetchone()
            cursor = connection.cursor()
            query = f"SELECT * FROM `{data_path}`"
            cursor.execute(query)
            column_names = [description[0] for description in cursor.description]
            data_table = cursor.fetchall()
            df = pd.DataFrame(data_table, columns=column_names)
        except Exception as e:
            raise e
        finally:
            connection.close()
        return df, question, answers.split(',')
    
    def get_database_info(self, ) -> int:
        """returns the question count from the database"""
        connection = sqlite3.connect(self.path)
        data: int = 0
        try:
            cursor = connection.cursor()
            query = f"SELECT COUNT(*) FROM qa_table"
            cursor.execute(query)
            data = int(cursor.fetchone()[0])
        except Exception as e:
            print(e)
        finally:
            connection.close()
        return data


if __name__ == "__main__":
    mydatabase = Database()
    # mydatabase.wtq_collector('/home/gabortoth/Dokumentumok/Data/WikiTableQuestions') # this is to upload data
    data_table, question, answers = mydatabase.get_question_with_table(0) # this is to get a specific data
    print(f"{data_table}\n\n{question}\n{answers}")
