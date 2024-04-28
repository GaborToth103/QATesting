from load_database import MyDatabase
from mylogger import MyLogger
import mymodels as mymodels
import sys

class Evaluate:
    def __init__(self) -> None:
        with open('data/model_list.txt', 'r') as file:
            self.model_urls = [line.strip() for line in file.readlines()]        

    def scoring_answers(self, truth: str, model_answer: str, model: mymodels.Model, database: MyDatabase):
        truth: str = str(truth.lower().strip())
        model_answer: str = str(model_answer.lower().strip())
        # database.check_sql_answer(model_answer, truth): # FIXME database is failing for some reason 
        if model_answer: # TODO good scoring function
            if model_answer in truth:
                model.score[0] += 1
            if truth in model_answer:
                model.score[1] += 1
        log.debug(f'Llama score updated: {model.score}')
    
    def logging_results(self, date, model_name, data_name, seed_count, table_count, min_prec, max_prec, duration):
        data_to_append = {
            "Date": date,
            "Model name": model_name,
            "Data name": data_name,
            "Seed Count": seed_count,
            "Table Count": table_count,
            "Minimum precision": min_prec,
            "Maximum precision": max_prec,
            "Duration (seconds)": duration
        }
        log.save_row_to_csv(data_to_append)
    
    def evaluate(self, database: MyDatabase, limit: int | None = None):
        for model_url in self.model_urls:
            evaluated_count = 0
            model = mymodels.ModelLlama(url=model_url)
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
            self.logging_results("today", model, "parquet", 1, evaluated_count, f"{(model.score[0] * 100 / evaluated_count):.0f}%", f"{(model.score[1] * 100 / evaluated_count):.0f}%", 0)
        return evaluated_count

if __name__ == "__main__":
    log = MyLogger()
    limit = 100
    if len(sys.argv) != 1 and sys.argv[-1].isdigit:
        limit = int(sys.argv[-1])
    log.info(f"Script started, limit set to {limit}")
    eva = Evaluate()
    mydatabase = MyDatabase()
    total = eva.evaluate(mydatabase, limit=limit)
    
