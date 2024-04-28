from load_database import MyDatabase
from mylogger import MyLogger
import mymodels as mymodels
import sys
import pandas as pd
import decorators
import re
import datetime

def clean_string(input_string):
    cleaned_string = re.sub(r"[^\w\s]", "", input_string)
    cleaned_string = cleaned_string.replace(" ", "")
    cleaned_string = cleaned_string.lower()
    return cleaned_string

class Evaluate:
    def __init__(self) -> None:
        self.model_rows = pd.read_csv('data/model_list.csv', index_col=0)

    def scoring_answers(self, truth: str, model_answer: str, model: mymodels.Model, database: MyDatabase):
        """ Scoring function to tell how the model performed on this task. Sets the model's score.

        Args:
            truth (str): The true answer.
            model_answer (str): The model answer that needs to be analyzed.
            model (mymodels.Model): The model.
            database (MyDatabase): The database to check SQL query.
        """
        
        truth: str = str(truth.lower().strip())
        model_answer: str = str(model_answer.lower().strip())
        # database.check_sql_answer(model_answer, truth): # FIXME database is failing for some reason 
        if model_answer: # TODO good scoring function
            if clean_string(model_answer) in clean_string(truth):
                model.score[0] += 1
            if clean_string(truth) in clean_string(model_answer):
                model.score[1] += 1
        log.debug(f'Llama score updated: {model.score}')
    
    def logging_results(self, date: str, model_name: str, data_name: str, seed_count: str, table_count: str, min_prec: str, max_prec: str, duration: str):
        data_to_append = {
            "Date": date,
            "Model name": model_name,
            "Data name": data_name,
            "Seed count": seed_count,
            "Table count": table_count,
            "Minimum precision": min_prec,
            "Maximum precision": max_prec,
            "Duration (seconds)": duration
        }
        log.save_row_to_csv(data_to_append)
    
    @decorators.measure_time
    def evaluate(self, database: MyDatabase, model_row: pd.Series, model, limit: int | None = None):
        evaluated_count = 0
        for index, row in enumerate(database.rows):
            log.debug(f'Current question: {index} of {len(database.rows)} (limit {limit})')
            try:
                table, question, truth = database.get_stuff(row)
            except Exception as e:
                log.error(e)
                continue
            try:
                database.fill_database(table)
                model_answer: str = model.generate_text(table, question)
                log.info(f'{question}: {truth}, {model_answer}')
                evaluated_count += 1
                self.scoring_answers(truth, model_answer, model, database)
                log.info(f"Scores from {evaluated_count}: llama({(model.score[1] * 100 / evaluated_count):.0f}%)")
                if limit and evaluated_count >= limit:
                    break
            except Exception as e:
                log.error(e)
        return evaluated_count

if __name__ == "__main__":
    log = MyLogger()
    limit = 10000
    if len(sys.argv) != 1 and sys.argv[-1].isdigit:
        limit = int(sys.argv[-1])
    log.info(f"Script started, limit set to {limit}")
    eva = Evaluate()
    mydatabase = MyDatabase()
    for index, model_row in eva.model_rows.iterrows():
        model = mymodels.ModelLlama(url=model_row['URL'], n_gpu_layers=model_row['Layer offset count'])
        evaluated_count, elapsed_time= eva.evaluate(mydatabase, model_row, model, limit=limit)
        seed_count = 1
        eva.logging_results(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(model), "parquet", seed_count, evaluated_count, f"{(model.score[0] * 100 / evaluated_count):.0f}%", f"{(model.score[1] * 100 / evaluated_count):.0f}%", f"{elapsed_time:.0f}")
