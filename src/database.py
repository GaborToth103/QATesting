import pandas as pd
import sqlite3
import os

class Database:
    def __init__(self, path: str = '/home/p_tabtg/llama_project/QATesting/data/database.db', qa_table_name: str = "qa_table") -> None:
        self.path = path
        self.qa_table_name = qa_table_name

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
            return self.fill_database(df, self.qa_table_name)            

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

    def fill_database(self, table: pd.DataFrame, table_name: str, if_exists = 'replace') -> str | None:
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
            table.to_sql(table_name, conn, if_exists=if_exists, index=False)
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

    def get_qa_table(self) -> pd.DataFrame:
        """Returns the full QA table.

        Returns:
            pd.DataFrame: The full QA table.
        """
        connection = sqlite3.connect(self.path)
        try:
            cursor = connection.cursor()
            query = f"SELECT * FROM {self.qa_table_name}"
            cursor.execute(query)
            column_names = [description[0] for description in cursor.description]
            data_table = cursor.fetchall()
            return pd.DataFrame(data_table, columns=column_names)
        finally:
            connection.close()

    def set_qa_table(self, df: pd.DataFrame):
        try:
            conn = sqlite3.connect('example.db')
            df.to_sql(self.qa_table_name, conn, if_exists='replace', index=False)
        finally:
            conn.close()

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
            query = f"SELECT utterance, context, targetValue FROM {self.qa_table_name} where id = 'nt-{id}'"
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
        try:
            cursor = connection.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.qa_table_name}';")
            table_exists = cursor.fetchone() is not None
            if table_exists:
                query = f"SELECT COUNT(*) FROM {self.qa_table_name}"
                cursor.execute(query)
                record_count = int(cursor.fetchone()[0])
            else:
                record_count = 0                
            return record_count
        except sqlite3.OperationalError as e:
            print(e) # If table does not exist
            raise e
        except Exception as e:
            print(e)
            raise e
        finally:
            connection.close()
    
    def generate_questions_table(self, table_name: str, table: pd.DataFrame, qa_pairs: list[tuple[str, list[str], str, str]], if_exists='replace') -> None:
        """Fills the database with the table name and it's table, with question and aswer pairs belonging to this table 

        Args:
            table_name (str): The table name
            table (pd.DataFrame): The table
            qa_pairs (list[tuple[str, str]]): the list of question/answer pairs
        """
        qa = {
            'id': [],
            'utterance': [],
            'context': [],
            'targetValue': [],
            'valid': [],
            'original': [],
        }
        
        if if_exists == 'replace':
            self.empty_database()
        
        question_count = self.get_database_info()
        for index, qa_pair in enumerate(qa_pairs):
            qa['id'].append(f'nt-{question_count + index}')
            qa['utterance'].append(qa_pair[0])
            qa['context'].append(table_name)
            qa['targetValue'].append(qa_pair[1])
            qa['valid'].append(qa_pair[2])
            qa['original'].append(qa_pair[3])
        qa_table = pd.DataFrame(qa)
                
        self.fill_database(table, table_name=table_name, if_exists='replace')
        self.fill_database(qa_table, table_name=self.qa_table_name, if_exists=if_exists)

    def empty_database(self):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        # Fetch all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Drop each table
        for table in tables:
            cursor.execute(f'DROP TABLE "{table[0]}";')
            print(f'Table {table[0]} dropped.')

        conn.commit()
        conn.close()
        print('All tables dropped. Database is now empty.')
        
if __name__ == "__main__":
    test_database_path = "data/test_database.db"
    wtq_path = '/home/gabortoth/Dokumentumok/Data/WikiTableQuestions'

    # TODO make sure the function takes a table, a section_tableno name, and a list of qa tuples.
    table = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
        'Age': [25, 30, 35, 40, 28],
        'Occupation': ['Engineer', 'Doctor', 'Artist', 'Lawyer', 'Scientist'],
        'Salary': [70000, 120000, 50000, 90000, 95000]
    })        
    qa = [('How old is alice?', '25'), ('What is the occupation of Bob?', 'Doctor'), ('Who earns 50000?','Charlie')]
    section_table_id = 'People_0'

    # Execution
    db = Database(test_database_path)    
    db.generate_questions_table(section_table_id, table, qa, 'replace')
    # Test
    for x in range(db.get_database_info()):
        table, question, answers = db.get_question_with_table(x)
        print(table, question, answers)
