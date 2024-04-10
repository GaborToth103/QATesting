from transformers import pipeline
import pandas as pd
import load_database
# import translate
import logging_file
import logging
import llama2
import sqlite3

logging_file.conf(file_path='docs\logs.log')

class Evaluate:
    """ Evaluation class for testing different models for evaluating tables."""    
    def __init__(self) -> None:
        self.score_tapas = [0, 0]    # Tapas score min-max
        self.score_tapax = [0, 0]    # Tapax score min-max
        self.score_llama = [0, 0]    # LLama2 score min-max

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

    def scoring_answers(self, answer: str, answer_a: str, answer_b: str, llama_answer: str):
        """ Evaluates the answers and also renders scores to them. If it contains the answer it gets a full point, if it is only partially then it can.

        Args:
            answer (str): The true answer that we have to make comparison with.
            answer_a (str): Tapas model answer.
            answer_b (str): Tapax model answer.
            llama_answer (str): LLama generative model answer.
        """
        answer: str = str(answer.lower().strip())
        if answer in answer_a or answer_a in answer:
            self.score_tapas[1] += 1
            if answer in answer_a:
                self.score_tapas[0] += 1
            logging.debug(f'Tapas score updated: {self.score_tapas}')
        if answer in answer_b or answer_b in answer:
            if answer in answer_b:
                self.score_tapax[0] += 1
            self.score_tapax[1] += 1
            logging.debug(f'Tapax score updated: {self.score_tapax}')
        if answer in llama_answer or llama_answer in answer:
            if answer in llama_answer:
                self.score_llama[0] += 1
            self.score_llama[1] += 1
            logging.debug(f'Llama score updated: {self.score_llama}')

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

    def evaluate(self, rows, tqa, tqb, limit: int | None = None):
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
                # question = self.back_and_forth_translate(question)
                answer_a: str = tqa(table=table, query=question)['cells'][0].lower().strip()
                answer_b: str = tqb(table=table, query=question)['answer'].lower().strip()                
                red_table = llama2.reduce_table_size(table)
                llama_answer: str = llama2.execute_steam(f"{red_table}\n{question} The answer is:")
                if self.check_sql_answer(llama_answer, answer):
                    print("yay")
                self.scoring_answers(answer, answer_a, answer_b, llama_answer)
                # logging.info(f"\n{question},({answer}, {answer_a}, {answer_b}, {llama_answer}))")
                if limit and index > limit:
                    break
            except Exception as e:
                logging.warning(e)
        return index

    def print_data(self, total):
        message = f"scores from {total}: tapas({(self.score_tapas[0] * 100 / total):.0f}%), tapax({(self.score_tapax[0] * 100 / total):.0f}%), llama({(self.score_llama[0] * 100 / total):.0f}%)"
        print(message)
        logging.info(message)
     

if __name__ == "__main__":
    eva = Evaluate()
    tqa, tqb = eva.initialize_model_pipelines()
    rows = load_database.extract(path_to_parquet='data/0000.parquet')
    total = eva.evaluate(rows, tqa, tqb, limit=500)
    eva.print_data(total)
