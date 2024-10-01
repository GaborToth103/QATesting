import pandas as pd
from database import Database
from models import ModelLlama, Prompt
from tqdm import tqdm
from mylogger import MyLogger
from utilities import *

class Controller:
    def __init__(self, model_list_path: str, data_path: str) -> None:
        self.database: Database = Database(path=data_path)
        self.model_details: pd.DataFrame = pd.read_csv(model_list_path, index_col=False)
        self.logger: MyLogger = MyLogger()

    @measure_time
    def evaluate_model(self, model: ModelLlama, seed_count: int, question_to_ask: int) -> list[float]:
        results: list[float] = list()
        for seed_index in range(seed_count):
            score = 0
            for data_index in tqdm(range(question_to_ask), unit="questions", desc=f"{model.name} {seed_index}"):
                table, question, truth = self.database.get_question_with_table(data_index)
                answer = model.generate_text(data_index, table.to_csv(index=False), question).split(',')
                # truth.append(translated_answers[data_index]) # FIXME hungarian translate hardcoded
                success = scoring(truth, answer)
                score += success
                self.logger.debug(f"{success}\t{question}\t{truth}\t{answer}")
            results.append(score/question_to_ask)
        return results     

    def loop(self, seed_count: int = 1, question_limit: int | None = None, language_en: bool = True):
        """The main loop. Loop through all questions"""
        question_count_to_ask: int = min(question_limit,self.database.get_database_info()) # get how many total questions to ask
        self.logger.info(f"New loop started with {seed_count} seed count, {question_count_to_ask} total questions and the language is en: {language_en}.")
        for model_detail in self.model_details.iterrows(): # loop through all models to ask questions from all of them
            try:
                # evaluation
                results, elapsed_time = self.evaluate_model(
                    ModelLlama(url=model_detail[1]['URL'], n_gpu_layers=int(model_detail[1]['Layer offset count']), prompt_format=Prompt(model_detail[1]['Prompt format'])),
                    seed_count,
                    question_count_to_ask)
                # logging
                self.logger.logging_results("WTQ", question_count_to_ask, language_en, model_detail[1]['Name'], question_count_to_ask/elapsed_time, results)
            except ValueError as context_size_violation:
                self.logger.error(context_size_violation)

if __name__ == "__main__":
    controller = Controller(
        model_list_path='data/model_list.csv',
        data_path='data/database.db',
    )
    controller.loop(
        seed_count=1,
        question_limit=10,
        language_en=True,
    )