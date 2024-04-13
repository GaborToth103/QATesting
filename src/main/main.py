from load_database import MyDatabase
from mylogger import MyLogger
import mymodels as mymodels
import sys

log = MyLogger()

class Evaluate:
    def __init__(self) -> None:
        self.model_llama = mymodels.ModelLlama()
        self.models = [self.model_llama]

    def scoring_answers(self, answer: str, llama_answer: str, model: mymodels.Model):
        answer: str = str(answer.lower().strip())
        if answer in llama_answer or llama_answer in answer:
            if answer in llama_answer:
                model.score[0] += 1
            model.score[1] += 1
            log.debug(f'Llama score updated: {self.model_llama.score}')
    
    def evaluate(self, database: MyDatabase, limit: int | None = None):
        for model in self.models:
            for index, row in enumerate(database.rows):
                try:
                    table, question, answer = database.get_stuff(row)
                except Exception as e:
                    print(e)
                    continue
                try:
                    log.debug(f'Current question: {index} of {len(database.rows)} (limit {limit})')
                    database.fill_database(table)
                    red_table = model.reduce_table_size(table)
                    llama_answer: str = model.generate_text((f"{red_table}\n{question}\nOnly the answer, no explanation. The answer:"))
                    log.info(f'{llama_answer}, {answer}')
                    if database.check_sql_answer(llama_answer, answer):
                        print("yay")
                    self.scoring_answers(answer, llama_answer, model)
                    self.print_data(index)
                    if limit and index > limit:
                        break
                except Exception as e:
                    log.warning(e)
        return index

    def print_data(self, total):
        message = f"scores from {total}: llama({(self.model_llama.score[0] * 100 / total):.0f}%)"
        print(message)
        log.info(message)
     

if __name__ == "__main__":
    limit = 10
    if len(sys.argv) != 1:
        limit = sys.argv[-1]
    eva = Evaluate()
    mydatabase = MyDatabase()
    total = eva.evaluate(mydatabase, limit=10)
    eva.print_data(total)
