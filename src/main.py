import re
import pandas as pd
from database import Database
from models import ModelLlama, Prompt
from tqdm import tqdm
from mylogger import MyLogger
from utilities import measure_time

class Controller:
    def __init__(self, model_list_path: str, data_path: str) -> None:
        self.database: Database = Database(parquet_path=data_path)
        self.model_details: pd.DataFrame = pd.read_csv(model_list_path, index_col=0)
        self.logger: MyLogger = MyLogger()

    @measure_time
    def evaluate_model(self, model: ModelLlama, seed_count: int, question_to_ask: int) -> list[float]:
        results: list[float] = list()
        for seed_index in range(seed_count):
            score = 0
            for data_index, data_entry in enumerate(tqdm(self.database.rows[:question_to_ask], unit="questions", desc=f"{model.name} {seed_index}")):
                table, question, truth = self.database.get_stuff(data_entry)
                answer = model.generate_text(data_index, table, question)
                success = self.scoring(truth, answer)
                if success: score += 1
                self.logger.debug(f"{success}\t{question}\t{truth}\t{answer}")
            results.append(score/question_to_ask)
        return results     

    def loop(self, seed_count: int = 1, question_limit: int | None = None, language_en: bool = True):
        question_to_ask: int = len(self.database.rows) if not question_limit else min(len(self.database.rows), question_limit)
        for model_index, model_detail in self.model_details.iterrows():
            try:
                model = None
                model = ModelLlama(url=model_detail['URL'], n_gpu_layers=int(model_detail['Layer offset count']), prompt_format=Prompt(model_detail['Prompt format']), lang_en=language_en)
                results, elapsed_time = self.evaluate_model(model, seed_count, question_to_ask)
                self.logger.logging_results(self.database.name, question_to_ask, language_en, model.name, question_to_ask/elapsed_time, results)
            except Exception as e:
                self.logger.error(e)

    @staticmethod
    def scoring(truth: str, model_answer: str) -> bool:
        """Scoring function to tell how the model performed on this task. The function cleans the strings and tokenizes them. If any of the truth's token is in the model_answer's token then we accept the answer.

        Args:
            truth (str): The true answer from the dataset accepted as truth to compare model answer with.
            model_answer (str): The model answer that needs to be analyzed.

        Returns:
            bool: the result whether the model_answer is accepted based on the truth.
        """        
        def clean_string(input_string: str) -> list[str]:
            cleaned_string = re.sub(r"[^\w\s]", "", input_string)
            cleaned_string = cleaned_string.lower()
            cleaned_list = cleaned_string.split()
            return cleaned_list
        
        if model_answer: #
            for truth_chunk in clean_string(truth):
                if truth_chunk in clean_string(model_answer):
                    return True
        return False

if __name__ == "__main__":
    controller = Controller(
        model_list_path='data/model_list.csv',
        data_path='data/wikitablequestions:test.parquet',
    )
    controller.loop(
        seed_count=10,
        question_limit=1000,
        language_en=True,
    )
    controller.loop(
        seed_count=10,
        question_limit=1000,
        language_en=False,
    )