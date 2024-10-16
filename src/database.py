import pandas as pd
import sqlite3
import os

class Database:
    def __init__(self, path: str = '/home/p_tabtg/llama_project/QATesting/data/database.db') -> None:
        self.path = path

    def dataframe_from_parquet(self, parquet_path: str) -> pd.DataFrame:
        """Generates dataframe from a parquet.

        Args:
            parquet_path (str): The path to the parquet.

        Returns:
            pandas.Dataframe: returns the parquet as pandas Dataframe.
        """
        df = pd.read_parquet(parquet_path)
        rows = []
        for index, row in df.iterrows():
            duplicate = len(df.columns) != len(df.columns.str.replace('.1$', '').drop_duplicates())
            if not duplicate:
                rows.append(row)
        return rows
    
    def wtq_collector(self, wtq_path: str) -> tuple[list, list]:
        """Filling the local sqlite3 database with WTQ tables and the QA Table to answer the questions

        Args:
            wtq_path (str): _description_

        Returns:
            tuple[list, list]: _description_
        """  
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
        """ Makes an SQL table based on the pandas table and pushes to the database.

        Args:
            table (pd.DataFrame): The table to use.
            table_name (str): The table name.

        Raises:
            pd.errors.DatabaseError: Returns the databaseError for possible problems.
        """
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

    def check_sql_answer(self, llm_answer: str, true_answer: str) -> bool:
        """Checks SQL answers from the database.

        Args:
            llm_answer (str): The model answer.
            true_answer (str): The truth.

        Returns:
            bool: Are they equal?
        """
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
        """Tries to fill the database"""
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
        """ From the id, get the table, the question and the answer as return values.

        Args:
            id (str): the id of the question

        Raises:
            Exception: raises all exception as it should not fail.

        Returns:
            tuple[pd.DataFrame, str, list[str]]: The table, the question and the answers.
        """
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
        truth = answers.split(',')
        answers = []     # '|' needs to be handled as separate answers
        for truth_chunk in truth:
            chunks = truth_chunk.split("|")
            answers += chunks
        
        
        return df, question, answers
    
    def get_database_info(self, ) -> int:
        """Returns the question count from the database.

        Returns:
            int: the question count.
        """
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
    
    def generate_questions_table(self, table: pd.DataFrame, qa_table: pd.DataFrame):
        self.fill_database(table, table_name="table")
        self.fill_database(qa_table, table_name="qa_table")

    def save_data_to_database(self, table: pd.DataFrame, question: str, answer: str):        
        raise NotImplementedError()


if __name__ == "__main__":
    # To fill wtq and get something:
    mydatabase = Database()
    mydatabase.wtq_collector('/home/p_tabtg/llama_project/data/WikiTableQuestions') # this is to upload data
    data_table, question, answers = mydatabase.get_question_with_table(0) # this is to get a specific data
    print(f"{data_table}\n\n{question}\n{answers}")
    exit()
    
    # To test the fictional database:
    
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
        'Age': [25, 30, 35, 40, 28],
        'Occupation': ['Engineer', 'Doctor', 'Artist', 'Lawyer', 'Scientist'],
        'Salary': [70000, 120000, 50000, 90000, 95000]
    }
    df = pd.DataFrame(data)
    qa = {
        'id': ['nt-0'],
        'utterance': ['asd'],
        'context': ['table'],
        'targetValue': ['0'],
    }    
    df2 = pd.DataFrame(qa)

    # To fill fictional and get something:
    mydatabase2 = Database("data/fictional.db")    
    mydatabase2.generate_questions_table(df, df2)
    data_table, question, answers = mydatabase2.get_question_with_table(0)
    print(f"{data_table}\n\n{question}\n{answers}")
