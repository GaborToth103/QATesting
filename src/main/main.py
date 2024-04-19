from load_database import MyDatabase
from mylogger import MyLogger
import mymodels as mymodels
import sys

class Evaluate:
    def __init__(self) -> None:
        self.model_llama = mymodels.ModelLlama()
        self.models = [self.model_llama]

    def scoring_answers(self, truth: str, model_answer: str, model: mymodels.Model):
        truth: str = str(truth.lower().strip())
        model_answer: str = str(model_answer.lower().strip())
        if truth in model_answer or model_answer in truth:
            if truth in model_answer:
                model.score[0] += 1
                model.score[1] += 1
            model.score[1] += 1
            log.debug(f'Llama score updated: {self.model_llama.score}')
    
    def evaluate(self, database: MyDatabase, limit: int | None = None):
        evaluated_count = 0
        for model in self.models:
            for index, row in enumerate(database.rows):
                log.debug(f'Current question: {index} of {len(database.rows)} (limit {limit})')
                try:
                    table, question, answer = database.get_stuff(row)
                except Exception as e:
                    print(e)
                    continue
                try:
                    database.fill_database(table)
                    answer: str = model.generate_text(table, question)
                    log.info(f'{answer}, {answer}')
                    if database.check_sql_answer(answer, answer):
                        print("yay")
                    evaluated_count += 1
                    self.scoring_answers(answer, answer, model)
                    log.info(f"Scores from {evaluated_count}: llama({(self.model_llama.score[0] * 100 / evaluated_count):.0f}%)")
                    if limit and evaluated_count >= limit:
                        break
                except Exception as e:
                    log.warning(e)
        return evaluated_count

if __name__ == "__main__":
    log = MyLogger()
    limit = 10
    if len(sys.argv) != 1 and sys.argv[-1].isdigit:
        limit = int(sys.argv[-1])
    log.info(f"Script started, limit set to {limit}")
    eva = Evaluate()
    mydatabase = MyDatabase()
    total = eva.evaluate(mydatabase, limit=limit)
