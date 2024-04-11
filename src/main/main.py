from transformers import pipeline
import pandas as pd
import load_database
# import translate
import logging_file
import logging
import template_prod
import sqlite3
import sys

logging_file.conf(file_path='docs\logs.log')

class Evaluate:
    """ Evaluation class for testing different models for evaluating tables."""    
    def __init__(self) -> None:
        self.model_llama = template_prod.ModelLlama()
        self.model_tapas = template_prod.ModelTapas()
        self.model_tapax = template_prod.ModelTapax()
        self.model_trans = template_prod.ModelTranslate()
        self.models = [self.model_llama, self.model_tapas, self.model_tapax]

    def back_and_forth_translate(self, question: str) -> str:
        """ Translating an english text to hungarian and back to english to simulate hungarian text being solved by these english only models.

        Args:
            question (str): The question to translate back and forth.

        Returns:
            str: the retranslated question.
        """
        # question = translate.translate_sentence(question, "hu")
        # question = translate.translate_sentence(question, "en")
        return question

    def scoring_answers(self, answer: str, llama_answer: str):
        """ Evaluates the answers and also renders scores to them. If it contains the answer it gets a full point, if it is only partially then it can.

        Args:
            answer (str): The true answer that we have to make comparison with.
            answer_a (str): Tapas model answer.
            answer_b (str): Tapax model answer.
            llama_answer (str): LLama generative model answer.
        """
        answer: str = str(answer.lower().strip())
        if answer in llama_answer or llama_answer in answer:
            if answer in llama_answer:
                self.model_llama.score[0] += 1
            self.model_llama.score[1] += 1
            logging.debug(f'Llama score updated: {self.model_llama.score}')

    def initialize_model_pipelines(self):
        """ Initialize models for evaluating tables. 

        Returns:
            _type_: the model references
        """
        model_a = "google/tapas-base-finetuned-wtq"
        model_b = "microsoft/tapex-base-finetuned-wtq"
        tqa = pipeline(task="table-question-answering", model=model_a)
        tqb = pipeline(task="table-question-answering", model=model_b)
        return tqa, tqb
    
    def check_sql_answer(self, llm_answer, true_answer):
        connection = sqlite3.connect('data/database.db')
        cursor = connection.cursor()
        result = cursor.execute(llm_answer)
        connection.close()
        return result.fetchone() == true_answer

    def evaluate(self, rows, limit: int | None = None):
        """ Evaluate tables for all models. Main function.

        Args:
            rows (_type_): Pandas rows of tables. It will get iterated row by row, it contains the table.
            tqa (_type_): _description_
            tqb (_type_): _description_
            limit (int | None, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        for index, row in enumerate(rows):
            try:
                logging.debug(f'Current question: {index} of {len(rows)} (limit {limit})')
                table, question, answer = load_database.get_stuff(row)
                load_database.fill_database(table)
                red_table = self.model_llama.reduce_table_size(table)
                llama_answer: str = self.model_llama.generate_text((f"{red_table}\n{question}\n"))
                logging.info(f'{llama_answer}, {answer}')
                if self.check_sql_answer(llama_answer, answer):
                    print("yay")
                self.scoring_answers(answer, llama_answer)
                self.print_data(index)
                if limit and index > limit:
                    break
            except Exception as e:
                logging.warning(e)
        return index

    def print_data(self, total):
        message = f"scores from {total}: llama({(self.model_llama.score[0] * 100 / total):.0f}%)"
        print(message)
        logging.info(message)
     

if __name__ == "__main__":
    limit = 10
    if len(sys.argv) != 1:
        limit = sys.argv[-1]
    eva = Evaluate()
    rows = load_database.extract(path='data/0000.parquet')
    total = eva.evaluate(rows, limit=10)
    eva.print_data(total)
