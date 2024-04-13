import logging
import os
import pandas as pd

class MyLogger(logging.getLoggerClass()):
    def __init__(self, name: str = "Evaluator Logger", level: int | str = 0, location = "docs/") -> None:
        super().__init__(name, level)
        self.location = location
        self.create_file_if_not_exists(self.location + "logs.log", True)
        self.create_file_if_not_exists(self.location + "result.csv", False)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)

        file_handler = logging.FileHandler(self.location + "logs.log")
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)

    def create_file_if_not_exists(self, relative_path, log_type: bool = True):
        current_directory = os.getcwd()
        file_path = os.path.join(current_directory, relative_path)

        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        try:
            # Try to create the file
            if log_type:
                with open(file=file_path, mode="w"):
                    pass
            else:
                row = pd.DataFrame(None, columns=["Date", "Model name", "Data name", "Seed count", 
                                                    "Table Count", "Minimum precision", "Maximum precision", 
                                                    "Duration (seconds)"])
                row.to_csv(file_path, mode='x', header=True, index=False, sep=";")  # Append row to the CSV file without writing headers
            print(f"File {file_path} created.")
        except Exception as e:
            print(f"Error creating file: {e}")
        return file_path

    def save_row_to_csv(self, data_to_append: dict, file_name: str = "result.csv"):
        path = self.location + file_name



        row = pd.DataFrame([data_to_append], columns=["Date", "Model name", "Data name", "Seed count", 
                                            "Table Count", "Minimum precision", "Maximum precision", 
                                            "Duration (seconds)"])

        row.to_csv(path, mode='a', header=False, index=False, sep=";")  # Append row to the CSV file without writing headers

if __name__ == "__main__":
    log = MyLogger()
    log.debug("hallo")
    data_to_append = {
    "Date": "2024-04-12",
    "Model name": "Example Model",
    "Data name": "Example Data",
    "Seed count": 123,
    "Table Count": 456,
    "Minimum precision": 0.95,
    "Maximum precision": 0.98,
    "Duration (seconds)": 123.45
    }
    log.save_row_to_csv(data_to_append)
