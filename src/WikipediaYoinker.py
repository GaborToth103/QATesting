import pandas as pd
import requests
from bs4 import BeautifulSoup
import re  # Import regular expressions for citation removal
from io import StringIO
from typing import Dict, List, Tuple
from database import Database
from transformers import pipeline
from mylogger import MyLogger
from openai_module import *
from report import Report
from tqdm import tqdm
from urllib.parse import unquote
from unidecode import unidecode
from enum import Enum, auto

class Algorithm(Enum):
    OPENAI = auto()
    ROBERTA = auto()


skip_sections = {'Kapcsolódó_szócikkek', 'mw-fr-revisionratings-box'}
hungarian_question_words = ['ki',
 'kik',
 'mi',
 'mik',
 'kit',
 'mit',
 'kivel',
 'mivel',
 'hol',
 'hová',
 'honnan',
 'mikor',
 'meddig',
 'mióta',
 'milyen gyakran',
 'hány',
 'mennyi',
 'hányszor']

class Section:    
    def __init__(self, section_name: str, raw_section_data: str) -> None:
        """A wikipedia section. Process raw section data into a paragraph/list of tables.

        Args:
            section_name (str): The name of the section
            raw_section_data (str): The raw data to make into a paragraph and list of tables
        """
        raw_section_data = self.remove_citations(raw_section_data)       
        self.section_name: str = section_name
        self.paragraph: str = self.extract_paragraph(raw_section_data)
        self.list_of_tables: list[pd.DataFrame] = self.extract_tables(raw_section_data)
        
    @staticmethod
    def analyse_subsection():
        # TODO
        raise NotImplementedError()
        
    def __str__(self) -> str:
        return self.section_name

    @staticmethod
    def remove_citations(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for cite in soup.find_all(class_='cite-bracket'):
            cite.decompose()
        for cite_ref in soup.find_all('sup', class_='reference'):
            cite_number = cite_ref.find('span', class_='cite-bracket')
            if cite_number:
                cite_number.extract()
            cite_ref.extract()
        cleaned_html = str(soup)
        return cleaned_html

    @staticmethod
    def convert_paragraph_to_hungarian_notation(text: str) -> str:
        # Regular expression to find numbers with commas
        def replace_match(match):
            return match.group(0).replace(',', '.')

        # Replace only numbers containing commas
        converted_text = re.sub(r'-?\d+,\d+', replace_match, text)
        return converted_text


    @staticmethod
    def clean_html(text):
        clean = re.compile('<.*?>')  # This regex pattern finds all HTML tags
        return re.sub(clean, '', text)

        
    @staticmethod
    def extract_paragraph(raw_section_data: str) -> str:
        """Extract the paragraphs (non-table string data) from the section and combines those into a large paragraph. 

        Args:
            raw_section_data (str): The h2 section chunk of a html page

        Returns:
            str: the combined paragraph 
        """
        paragraphs = []
        while True:
            p_start = raw_section_data.find('<p')
            if p_start == -1:
                break  # No more <p> tags

            p_end = raw_section_data.find('</p>', p_start) + len('</p>')
            paragraph = raw_section_data[p_start:p_end]  # Extract the <p> tag content
            paragraphs.append(paragraph)

            # Remove the processed paragraph from section_content
            raw_section_data = raw_section_data[p_end:]

        # Unite paragraphs into plain text
        plain_text: str = ' '.join(paragraphs).replace('<p>', '').replace('</p>', '').strip()

        plain_text = Section.clean_html(plain_text)
        plain_text = Section.convert_paragraph_to_hungarian_notation(plain_text)


        return plain_text
        

    @staticmethod
    def extract_tables(raw_section_data: str) -> list[pd.DataFrame]:
        """Extract tables of a section data.

        Args:
            raw_section_data (str): The section chunk of a html page

        Returns:
            list[pd.DataFrame]: list of tables in pandas dataframe format.
        """

        try:
            tables = pd.read_html(StringIO(raw_section_data), decimal=",", thousands=" ")
            for table in tables:
                table = table.apply(pd.to_numeric, errors='coerce')
                table = table.map(lambda x: str(x).replace('.', ',') if isinstance(x, (int, float, str)) else x)
                return tables
        except ValueError:
            # If no tables were found in this section, continue
            return []

class WikiYoinker:
    def __init__(self,  logger: MyLogger, starting_page_name: str = "Szeged", language_code: str = "hu", use_openai: bool = False, strict: bool = True) -> None:
        self.logger = logger
        self.use_openai = use_openai
        self.strict = strict
        self.unmasker = pipeline('fill-mask', model='xlm-roberta-base')
        self.starting_page_title = starting_page_name
        self.language_code = language_code

    @staticmethod
    def url_exists_in_canonicals(existing_canonicals: list[str], title: str, language_code: str = "hu") -> bool:
        """Takes the title (like "Szeged") and constructs the full URL by appending it to the base Wikipedia URL. Checks if the full canonical URL exists in the list existing_canonicals.

        Args:
            existing_canonicals (list[str]): list of wikipedia titles already processed
            title (str): the wikipedia title to check

        Returns:
            bool: whether the url exists or not.
        """
        base_url = f"https://{language_code}.wikipedia.org/wiki/"
        url = base_url + title
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            canonical_link = soup.find("link", rel="canonical")
            canonical_url = canonical_link['href'] if canonical_link else url
        except (requests.RequestException, KeyError):
            canonical_url = url
        if canonical_url in existing_canonicals:
            return True
        return False


    def yoink_page(self, url: str) -> tuple[list[pd.DataFrame], list[str]]:
        """This function should get the whole page and separate tables and the page text as return"""
        
        response = requests.get(url)
        tables: list[pd.DataFrame] = pd.read_html(StringIO(response.text))
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find_all(['p'])
        text = "\n".join([tag.get_text(strip=False) for tag in content])
        sentences = re.sub(r'\[\d+\]', '', text).strip().replace("\n", " ").replace("  ", " ").split(". ")
        return tables, [s.strip() for s in sentences]

    @staticmethod
    def sectioning(raw_section_data: str) -> list[str]:
        """Separate sectioning function to be able to be used with string that outputs raw list of header3 data subsets.

        Args:
            raw_section_data (str): Raw html data subset that represents a Header2 section

        Raises:
            NotImplementedError: TODO 

        Returns:
            list[str]: _description_
        """
        raise NotImplementedError()

    def convert_url_to_section_data(self, url: str) -> list[Section]:
        """Splits URL content into section chunks with section id.

        Args:
            url (str): the URL to convert

        Returns:
            list[Section]: list of sections in the url
        """
        response = requests.get(url)
        text = response.text.replace("–", "-")

        # Split the response into chunks by <h2> sections
        sections = text.split('<h2')

        # Dictionary to store tables by section id
        section_objs: list[Section] = []

        for section in sections[1:-1]:  # Skip the first chunk since it is before the first <h2>
            section = '<h2' + section  # Prepend <h2> to the section again

            # Find the ID of the <h2> tag, assuming format <h2 id="section_id">
            id_start = section.find('id="') + len('id="')
            id_end = section.find('"', id_start)
            section_id = section[id_start:id_end]  # Extract the id of the <h2> tag
            
            # Skip bannde section titles
            if section_id in skip_sections:
                continue

            # Find the end of the <h2> tag
            end_of_h2 = section.find('</h2>') + len('</h2>')

            # Extract the part of the section after the <h2> header
            section_content = section[end_of_h2:]
            
            new_section = Section(section_name=section_id, raw_section_data=section_content)
            section_objs.append(new_section)

        return section_objs

    @staticmethod
    def get_next_500_page(starting_page: str, language_code = "hu") -> list[str]:
        S = requests.Session()

        PARAMS = {
            "action": "query",
            "format": "json",
            "list": "allpages",
            "apfrom": starting_page,
            "aplimit": 500,
        }

        api_url = f"https://{language_code}.wikipedia.org/w/api.php"

        R = S.get(url=api_url, params=PARAMS)
        data = R.json()
        titles = []
        for next_page in data["query"]["allpages"]:
            title = next_page['title']
            titles.append(title)


        return titles[:-1], titles[-1]

    def get_next_page(self) -> requests.Request:

        def get_next_page(apfrom: str):
            return apfrom

        S = requests.Session()

        PARAMS = {
            "action": "query",
            "format": "json",
            "list": "allpages",
            "apfrom": get_next_page(self.starting_page_title),
            "aplimit": 2,
        }

        api_url = f"https://{self.language_code}.wikipedia.org/w/api.php"

        R = S.get(url=api_url, params=PARAMS)
        data = R.json()
        next_page_title = data["query"]["allpages"][0]["title"]
        self.starting_page_title = data["query"]["allpages"][1]["title"]

        page_url = f"https://hu.wikipedia.org/wiki/{next_page_title}"

        request = requests.get(page_url)
        return request

    def extract_tables_by_h2(self, url: str) -> Dict[str, List[pd.DataFrame]]:
        """extract tables for each section. Currently is not working as intended."""
        # Fetch the response
        response = requests.get(url)

        # Split the response into chunks by <h2> sections
        sections = response.text.split('<h2')

        # Dictionary to store tables by section id
        tables_by_section = {}

        for section in sections[1:]:  # Skip the first chunk since it is before the first <h2>
            section = '<h2' + section  # Prepend <h2> to the section again

            # Find the ID of the <h2> tag, assuming format <h2 id="section_id">
            id_start = section.find('id="') + len('id="')
            id_end = section.find('"', id_start)
            section_id = section[id_start:id_end]  # Extract the id of the <h2> tag

            # Find the end of the <h2> tag
            end_of_h2 = section.find('</h2>') + len('</h2>')

            # Extract the part of the section after the <h2> header
            section_content = section[end_of_h2:]

            # Attempt to extract tables from the current section
            try:
                tables = pd.read_html(StringIO(section_content), decimal=",", thousands=" ")
                for table in tables:
                    table = table.apply(pd.to_numeric, errors='coerce')
                    table = table.map(lambda x: str(x).replace('.', ',') if isinstance(x, (int, float, str)) else x)
                tables_by_section[section_id] = tables  # Store tables under the section id
            except ValueError:
                # If no tables were found in this section, continue
                continue

        return tables_by_section

    def extract_paragraphs_by_h2(self, url: str) -> Dict[str, str]:
        # Fetch the response
        response = requests.get(url)

        # Split the response into chunks by <h2> sections
        sections = response.text.split('<h2')

        # Dictionary to store paragraphs by section id
        paragraphs_by_section = {}

        for section in sections[1:]:  # Skip the first chunk since it is before the first <h2>
            section = '<h2' + section  # Prepend <h2> to the section again

            # Find the ID of the <h2> tag
            id_start = section.find('id="') + len('id="')
            id_end = section.find('"', id_start)
            section_id = section[id_start:id_end]  # Extract the id of the <h2> tag

            # Find the end of the <h2> tag
            end_of_h2 = section.find('</h2>') + len('</h2>')

            # Extract the part of the section after the <h2> header
            section_content = section[end_of_h2:]

            # Extract <p> tags
            paragraphs = []
            while True:
                p_start = section_content.find('<p')
                if p_start == -1:
                    break  # No more <p> tags

                p_end = section_content.find('</p>', p_start) + len('</p>')
                paragraph = section_content[p_start:p_end]  # Extract the <p> tag content
                paragraphs.append(paragraph)

                # Remove the processed paragraph from section_content
                section_content = section_content[p_end:]

            # Unite paragraphs into plain text
            plain_text = ' '.join(paragraphs).replace('<p>', '').replace('</p>', '').strip()
            paragraphs_by_section[section_id] = plain_text  # Store plain text under the section id

        return paragraphs_by_section

    def find_matching_words(self, paragraph: str, table: pd.DataFrame) -> List[Dict[str, Tuple[int, int, str]]]:
        """ takes a paragraph string and a Pandas DataFrame as input and returns a list of coordinate/sentence pairs where words from the DataFrame match words in the paragraph."""
        # TODO ha kétszer szerepel ugyanaz a szó a táblázatban, csak az elsőt válasszuk
        # Preprocess the paragraph to get sentences and words
        if self.strict:
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)  # Split paragraph with less stuff to split by: larger sentences
        else:
            sentences = re.split(r'(?<=[.!?;,])\s+', paragraph)  # Split paragraph into sentences
            larger_sentences = re.split(r'(?<=[.!?])\s+', paragraph)  # Split paragraph with less stuff to split by: larger sentences
            sentences = list(set(sentences + larger_sentences)) # combine both without duplicates
        # Create a set of words in the paragraph for exact matching
        words_in_paragraph = set(re.findall(r'\b\w+(?:\.\w+)?\b', paragraph.lower()))

        # Store results
        results = []
        
        # TODO
        cell_dict = {}
        for i, row in table.iterrows():
            for j, cell in enumerate(row):
                cell_str2 = str(cell).strip().lower()
                cell_dict[cell_str2] = (i, j)
                
        for cell_str, coordinate in cell_dict.items():
            if cell_str in [s.lower() for s in sentences]:  
                for sentence in sentences:
                    if sentence.lower() == cell_str:
                        results.append({
                            'cell_coordinates': coordinate,
                            'matching_sentence': sentence
                        })

            else:
                # Check for any word matches (not complete sentences)
                if cell_str in words_in_paragraph:
                    for sentence in sentences:
                        words_in_sentence = set(re.findall(r'\b\w+(?:\.\w+)?\b', sentence.lower()))
                        if cell_str in words_in_sentence:
                            results.append({
                                'cell_coordinates': coordinate,
                                'matching_sentence': sentence
                            })

        return results
    
    def convert_paragraph_to_hungarian_notation(self, text: str) -> str:
        # Regular expression to find numbers with commas
        def replace_match(match):
            return match.group(0).replace(',', '.')

        # Replace only numbers containing commas
        converted_text = re.sub(r'-?\d+,\d+', replace_match, text)
        return converted_text

    def clean_html(self, text):
        clean = re.compile('<.*?>')  # This regex pattern finds all HTML tags
        return re.sub(clean, '', text)
    
    def transform_statement_to_question(self, statement: str, word: str) -> tuple[str, bool]:        
        """Given a statement with a word, where the word must be masked and we need to replace dot with questionmark at the end."""
        mask_string = "<mask>"
        masked_question = statement.replace(word, mask_string)[:-1] + "?"
        mask_count = masked_question.count(mask_string)
        if mask_count != 1:
            self.logger.debug("Multiple answer word found in the sentence.")
            return None, False
        
        if not self.use_openai:
            answer = self.unmasker(f"Kérdés: {masked_question}\nVálasz: {word}.")
            valid_token = self.has_question_candidates(answer)
            if valid_token:
                return masked_question.replace(mask_string, valid_token)[:-1] + "?", True
            self.logger.debug(f"No valid solution found: {answer}")
            return masked_question.replace(mask_string, answer[0]['token_str'].lower())[:-1] + "?", False
        else:
            question, valid = generate_question_from_sentence_openai(statement, word)
            return question, valid
    
    def has_question_candidates(self, answers: list[dict]) -> str | None:
        """Checks if the answer has any token string that is equal to a hungarian question word.

        Args:
            answer (list[dict]): the answer from a ROBERTA model

        Returns:
            bool: if any of the answer[x]['token_str'] variable is in the hqw table  
        """
        for answer in answers:
            if answer['token_str'].lower() in hungarian_question_words:
                return answer['token_str']
        return None
    
    def process_sections(self, sections: list[Section], logger, database, url: str, use_only_numbers: bool = False, skip_everything: bool = False):
        for section in sections:
            for index, table_section in enumerate(section.list_of_tables):
                results = self.find_matching_words(section.paragraph, table_section)
                for result in results:
                    row, col = result['cell_coordinates']
                    statement = result['matching_sentence'].lower().strip()
                    word = str(table_section.iat[row, col]).lower().strip()
                    if use_only_numbers:
                        try:
                            float(word)
                        except:
                            continue                    
                    try:
                        if skip_everything:
                            raise Exception("Skipped")
                        question, valid = self.transform_statement_to_question(statement, word)
                        logger.info(f"{section}(Szekció)\t{word}(Cella)\t{statement}(Mondat)\t{question}(Kérdés)\n{table_section}\n")
                    except Exception as e:
                        logger.debug(e)
                        valid = False
                        question = "e"
                    replaced_url = url.split("/")[-1].replace("–", "-").encode('ascii', 'replace').decode('ascii')
                    db_name = f'{replaced_url}_{section}_{index}'
                    database.generate_questions_table(db_name, table_section, [(question, word, valid, statement)], if_exists='append')


    def algorithm_generate_question(self, statement: str, answer: str, algorithm_type: Algorithm = Algorithm.ROBERTA) -> str:
        """Generate question with the selected algorithm based on the statement and an answer.

        Args:
            statement (str): The statement which is a complete sentence, it makes sense by itself.
            answer (str): The one word in the statement that is the answer. The algorithm must mask this and must create a question that this might be the answer to it.
            algorithm_type (Algorithm, optional): The algorithm used to generate a question. Defaults to Algorithm.ROBERTA.

        Raises:
            NotImplementedError: if the algorithm is not implemented, it throws this error.

        Returns:
            str: The question in string format.
        """

        if statement.count(answer) != 1:
            return "Multiple answer word found in the sentence.", False

        match algorithm_type:
            case Algorithm.OpenAI:
                return generate_question_from_sentence_openai(statement, answer)
            case Algorithm.ROBERTA:
                mask_string = "<mask>"
                masked_question = statement.replace(answer, mask_string)[:-1] + "?"               
                question = self.unmasker(f"Kérdés: {masked_question}\nVálasz: {answer}.")
                valid_token = self.has_question_candidates(question)
                if valid_token:
                    return masked_question.replace(mask_string, valid_token)[:-1] + "?", True
                self.logger.debug(f"No valid solution found: {question}")
                return masked_question.replace(mask_string, question[0]['token_str'].lower())[:-1] + "?", False

        raise NotImplementedError(f"{algorithm_type} algorithm handling is not implemented.")

    def algorithm_db_rework(self, database: Database, algorithm_type: Algorithm = Algorithm.ROBERTA):
        """Select an algorithm and a database, then the algorithm fills the database with questions. The questions will be overwritten!

        Args:
            database (Database): the database path filled with statements and answers with or without questions.
            algorithm_type (Algorithm, optional): The algorithm used to fill the database. Defaults to Algorithm.ROBERTA.
        """
        qa_table: pd.DataFrame = database.get_qa_table()
        for index, row in qa_table.iterrows():
            statement = row['original']
            answer = row['targetValue']
            question = self.algorithm_generate_question(statement, answer, algorithm_type)
            qa_table.loc[index, 'utterance'] = question
        database.set_qa_table(qa_table)


def fill_database():
    data_path = "data/generated_hu.db"
    starting_page = "Szeged"
    log_path = 'data/wiki.log'
    batch_count = 7
    
    database = Database(data_path)
    database.empty_database()
    logger: MyLogger = MyLogger(log_path=log_path, result_path=log_path)    
    wikiyoinker = WikiYoinker(starting_page_name=starting_page, use_openai=False, strict=True, logger=logger)
    for x in range(batch_count):
            pages, starting_page = wikiyoinker.get_next_500_page(starting_page, "hu")
            for page in tqdm(pages, desc=f"batch no. {x}."):
                try:
                    page_url = f"https://hu.wikipedia.org/wiki/{page}"
                    req = requests.get(page_url)
                    url = unquote(req.url)
                    sections = wikiyoinker.convert_url_to_section_data(url)
                    wikiyoinker.process_sections(sections, logger, database, url, skip_everything=True)
                except Exception as e:
                    logger.warning(e)
    Report().create_report_from_db()
    
def run_algorithm():
    data_path = "data/generated_hu.db"
    log_path = 'data/wiki.log'    
    database = Database(data_path)
    logger: MyLogger = MyLogger(log_path=log_path, result_path=log_path)    
    wikiyoinker = WikiYoinker(logger=logger)
    wikiyoinker.algorithm_db_rework(database, Algorithm.ROBERTA)
    

if __name__ == "__main__":
    fill_database()
    run_algorithm()