from load_database import MyDatabase
from mylogger import MyLogger
import mymodels as mymodels
import pandas as pd
import decorators
import re

class Evaluate:
    def __init__(self, model_list_path: str) -> None:
        """Evaluation function to get all models from a CSV to get questioned. The results will be logged to the target CSV.

        Args:
            model_list_path (str): The path of the CSV list of models with their descriptions.
            limit (int | None, optional): The maximum number of questions if we don't want to iterate through the whole dataset. Defaults to None.
        """
        self.log: MyLogger = MyLogger()
        self.mydatabase: MyDatabase = MyDatabase()
        self.model_rows: pd.DataFrame = pd.read_csv(model_list_path, index_col=0)
        self.model: mymodels.ModelLlama | None = None

    def scoring(self, truth: str, model_answer: str) -> bool:
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
            if clean_string(model_answer) in clean_string(truth) or clean_string(truth) in clean_string(model_answer):
                self.model.score[0] += 1
                self.model.score[1] += 1
                return True
        return False
        
    @decorators.measure_time
    def evaluate(self, model_row: pd.Series, seed_count: int = 1, limit: int | None = None) -> dict:
        min_accuracy = 1
        max_accuracy = 0
        for seed_index in range(seed_count):
            self.model.score = [0, 0]
            evaluated_count = 0
            for index, row in enumerate(self.mydatabase.rows):
                try:
                    table, question, truth = self.mydatabase.get_stuff(row)
                except Exception as e:
                    self.log.error(e)
                    continue
                try:
                    # self.mydatabase.fill_database(table) # FIXME database filling for SQL
                    model_answer: str = self.model.generate_text(index, table, question)
                    evaluated_count += 1
                    success: bool = self.scoring(truth, model_answer)
                    model_answer_format = model_answer.replace("\n", " ")
                    self.log.info(f'{evaluated_count}/{limit}\t{success}\t{question}\t{truth}\t{model_answer_format}')
                    if limit and evaluated_count >= limit:
                        break
                except Exception as e:
                    self.log.error(e)
            score = self.model.score[0] / evaluated_count
            self.log.info(f"{self.model.name} seed score\t{self.model.score[0]}/{evaluated_count}\t({(score*100):.0f}%)")
            max_accuracy = max(score, max_accuracy)
            min_accuracy = min(score, min_accuracy)
        result: dict = {
            "evaluated_count": evaluated_count,
            "min_accuracy": min_accuracy,
            "max_accuracy": max_accuracy
        }
        return result

    def iterate(self, seed_count: int = 1, lang_en: bool = True, limit: int | None = None):
        for index, model_row in self.model_rows.iterrows():
            self.model = None
            self.model = mymodels.ModelLlama(url=model_row['URL'], n_gpu_layers=int(model_row['Layer offset count']), prompt_format=mymodels.Prompt(model_row['Prompt format']), lang_en=lang_en)
            evaluation_result, elapsed_time = self.evaluate(model_row, seed_count, limit)
            self.log.logging_results(str(self.model), "wikitablequestions:test", seed_count, evaluation_result['evaluated_count'], evaluation_result['min_accuracy'], evaluation_result['max_accuracy'], elapsed_time, lang_en)

if __name__ == "__main__":
    Evaluate(model_list_path='data/model_list.csv').iterate(seed_count=3, lang_en=True, limit=100)