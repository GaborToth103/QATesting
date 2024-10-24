import logging
import os
import pandas as pd
import datetime

class MyLogger(logging.getLoggerClass()):
    def __init__(self, name: str = "Logger", level: int | str = 0, log_path = "/home/p_tabtg/llama_project/QATesting/data/logs.log", result_path = "/home/p_tabtg/llama_project/QATesting/data/result.csv") -> None:
        super().__init__(name, level)
        
        self.log_path = log_path
        self.result_path = result_path        
        self.create_file_if_not_exists(log_path, True)
        self.create_file_if_not_exists(result_path, False)
        
        formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel("WARNING")
        self.addHandler(console_handler)

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)

    def create_file_if_not_exists(self, relative_path: str, log_type: bool = True) -> str:
        """Create the log file if it's empty or non-existent.

        Args:
            relative_path (str): The relative path to the log file.
            log_type (bool, optional): The log type. Defaults to True.

        Returns:
            str: the absolute file path.
        """
        current_directory = os.getcwd()
        file_path = os.path.join(current_directory, relative_path)

        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(file_path):
            try:
                if log_type:           
                    with open(file=file_path, mode="w"):
                        pass
                else:
                    row = pd.DataFrame(None, columns=["Date", "Model name", "Data name", "Table count", "Accuracies", 
                                                        "Iteration speed", "Data language"])
                    row.to_csv(file_path, mode='x', header=True, index=False, sep=";")  # Append row to the CSV file without writing headers
                print(f"File {file_path} created.")
            except Exception as e:
                print(f"Error creating file: {e}")
        return file_path

    def logging_results(self, dataset_name: str, dataset_size: int, dataset_language_en: bool, model_name: str, iteration_speed: float, results: list[float]):
        """Logging results to the file.

        Args:
            dataset_name (str): The dataset name
            dataset_size (int): The question count.
            dataset_language_en (bool): If the language is english or not.
            model_name (str): The model name that was evaluated.
            iteration_speed (float): The speed of an evaluation (how many questions the model answered per second).
            results (list[float]): The accuracies of each seed in the model. 
        """
        data_to_append = {
            "Date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "Dataset name": dataset_name,
            "Dataset size": dataset_size,
            "Dataset language": "English" if dataset_language_en else "Hungarian",
            "Model name": model_name,
            "Iteration speed": f"{iteration_speed:.2f}",
            "Score": "[" + ", ".join([format(num, f".3f") for num in results]) + "]",
        }
        
        row = pd.DataFrame([data_to_append], columns=["Date", "Dataset name", "Dataset size", "Dataset language", "Model name", "Iteration speed", "Score"])
        row.to_csv(self.result_path, mode='a', header=False, index=False, sep=";")  # Append row to the CSV file without writing headers
        self.info(data_to_append)

    def make_report(self):
        """TODO make a html report from the available .csv file with plot"""
        raise NotImplementedError

if __name__ == "__main__":
    # MyLogger().make_report()
    MyLogger(log_path="data/asd.log", result_path="data/asd.log").info("haló")