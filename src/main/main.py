from load_database import MyDatabase
from mylogger import MyLogger
import mymodels as mymodels
import sys
import pandas as pd
import decorators
import re
import datetime

class Evaluate:
    def __init__(self, model_list_path: str, limit: int | None = None) -> None:
        """Evaluation function to get all models from a CSV to get questioned. The results will be logged to the target CSV.

        Args:
            model_list_path (str): The path of the CSV list of models with their descriptions.
            limit (int | None, optional): The maximum number of questions if we don't want to iterate through the whole dataset. Defaults to None.
        """
        self.limit: int = limit
        self.log: MyLogger = MyLogger()
        self.mydatabase: MyDatabase = MyDatabase()
        self.model_rows: pd.DataFrame = pd.read_csv(model_list_path, index_col=0)
        self.model: mymodels.Model = mymodels.Model()

    def scoring(self, truth: str, model_answer: str):
        """ Scoring function to tell how the model performed on this task. Sets the model's score.

        Args:
            truth (str): The true answer.
            model_answer (str): The model answer that needs to be analyzed.
        """
        def clean_string(input_string):
            cleaned_string = re.sub(r"[^\w\s]", "", input_string)
            cleaned_string = cleaned_string.replace(" ", "")
            cleaned_string = cleaned_string.lower()
            return cleaned_string
        
        truth: str = str(truth.lower().strip())
        model_answer: str = str(model_answer.lower().strip())
        # database.check_sql_answer(model_answer, truth): # FIXME database is failing for some reason 
        if model_answer: # TODO good scoring function
            if clean_string(model_answer) in clean_string(truth):
                self.model.score[0] += 1
            if clean_string(truth) in clean_string(model_answer):
                self.model.score[1] += 1
        self.log.debug(f'Llama score updated: {self.model.score}')
        
    @decorators.measure_time
    def evaluate(self, model_row: pd.Series, seed_count: int = 1) -> dict:
        min_accuracy = 1
        max_accuracy = 0
        for seed_index in range(seed_count):
            evaluated_count = 0
            for index, row in enumerate(self.mydatabase.rows):
                self.log.debug(f'Current question: {index} of {len(self.mydatabase.rows)} (limit {self.limit})')
                try:
                    table, question, truth = self.mydatabase.get_stuff(row)
                except Exception as e:
                    self.log.error(e)
                    continue
                try:
                    self.mydatabase.fill_database(table)
                    model_answer: str = self.model.generate_text(table, question)
                    self.log.info(f'{question}: {truth}, {model_answer}')
                    evaluated_count += 1
                    self.scoring(truth, model_answer)
                    self.log.info(f"Scores from {evaluated_count}: llama({(self.model.score[1] * 100 / evaluated_count):.0f}%)")
                    if self.limit and evaluated_count >= self.limit:
                        break
                except Exception as e:
                    self.log.error(e)
            score = self.model.score[1] / evaluated_count
            max_accuracy = max(score, max_accuracy)
            min_accuracy = min(score, min_accuracy)
        result: dict = {
            "evaluated_count": evaluated_count,
            "min_accuracy": min_accuracy,
            "max_accuracy": max_accuracy
        }
        return result

    def iterate(self, seed_count: int = 1):
        for index, model_row in self.model_rows.iterrows():
            self.model = mymodels.ModelLlama(url=model_row['URL'], n_gpu_layers=int(model_row['Layer offset count']))
            evaluation_result, elapsed_time = self.evaluate(model_row, seed_count=seed_count)
            self.log.logging_results(str(self.model), "parquet", seed_count, evaluation_result['evaluated_count'], evaluation_result['min_accuracy'], evaluation_result['max_accuracy'], elapsed_time)

if __name__ == "__main__":
    Evaluate(model_list_path='data/model_list.csv', limit=100).iterate(seed_count=1)