import pandas as pd
import os

def get_tables(dir_path = 'QuestionAnswering\Tables'):
    tables = []
    for file_path in os.listdir(dir_path):
        folder = os.path.join(dir_path, file_path)
        if os.path.isfile(folder):
            data_table = pd.read_json(dir_path + "\\" + file_path, dtype=False)
            tables.append(data_table)
        else:
            question = []
            table = []
            for file in os.listdir(folder):
                match file:
                    case "questions.json":
                        question = pd.read_json(folder + "\\" + file, dtype=False)
                    case "table.json":
                        table = pd.read_json(folder + "\\" + file, dtype=False)
            tables.append({"questions": question, "table": table})        
    return tables


def print_data(table: pd.core.frame.DataFrame):
    print(table._data)
    print(table.index)
    print(table.columns)
    print(table.dtypes)
    print(table.copy)


if __name__ == "__main__":
    print(get_tables())
