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
    def __init__(self, starting_page_name: str = "Szeged", language_code: str = "hu") -> None:
        self.unmasker = pipeline('fill-mask', model='xlm-roberta-base')
        self.starting_page_title = starting_page_name
        self.language_code = language_code



    def yoink_page(self, url: str) -> tuple[list[pd.DataFrame], list[str]]:
        """This function should get the whole page and separate tables and the page text as return"""
        
        response = requests.get(url)
        tables: list[pd.DataFrame] = pd.read_html(StringIO(response.text))
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find_all(['p'])
        text = "\n".join([tag.get_text(strip=False) for tag in content])
        sentences = re.sub(r'\[\d+\]', '', text).strip().replace("\n", " ").replace("  ", " ").split(". ")
        return tables, [s.strip() for s in sentences]

    def convert_url_to_section_data(self, url: str) -> list[Section]:
        """Splits URL content into section chunks with section id.

        Args:
            url (str): the URL to convert

        Returns:
            list[Section]: list of sections in the url
        """
        response = requests.get(url)

        # Split the response into chunks by <h2> sections
        sections = response.text.split('<h2')

        # Dictionary to store tables by section id
        section_objs: list[Section] = []

        for section in sections[1:]:  # Skip the first chunk since it is before the first <h2>
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

    def get_next_500_page(self) -> list[str]:
        raise NotImplementedError()

    def get_next_page(self) -> requests.Request:
        api_url = f"https://{self.language_code}.wikipedia.org/w/api.php"

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

    def find_matching_words(self, paragraph: str, table: pd.DataFrame, strict: bool = True) -> List[Dict[str, Tuple[int, int, str]]]:
        """ takes a paragraph string and a Pandas DataFrame as input and returns a list of coordinate/sentence pairs where words from the DataFrame match words in the paragraph."""
        # Preprocess the paragraph to get sentences and words
        if strict:
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)  # Split paragraph with less stuff to split by: larger sentences
        else:
            sentences = re.split(r'(?<=[.!?;,])\s+', paragraph)  # Split paragraph into sentences
            larger_sentences = re.split(r'(?<=[.!?])\s+', paragraph)  # Split paragraph with less stuff to split by: larger sentences
            sentences = list(set(sentences + larger_sentences)) # combine both without duplicates
        # Create a set of words in the paragraph for exact matching
        words_in_paragraph = set(re.findall(r'\b\w+(?:\.\w+)?\b', paragraph.lower()))

        # Store results
        results = []
        
        # Check each cell in the DataFrame
        for i, row in table.iterrows():
            for j, cell in enumerate(row):
                # Normalize the cell and check for exact matches
                cell_str = str(cell).strip().lower()
                
                # Check if the cell itself is an exact match with any sentence
                if cell_str in [s.lower() for s in sentences]:  
                    for sentence in sentences:
                        if sentence.lower() == cell_str:
                            results.append({
                                'cell_coordinates': (i, j),
                                'matching_sentence': sentence
                            })

                else:
                    # Check for any word matches (not complete sentences)
                    if cell_str in words_in_paragraph:
                        for sentence in sentences:
                            words_in_sentence = set(re.findall(r'\b\w+(?:\.\w+)?\b', sentence.lower()))
                            if cell_str in words_in_sentence:
                                results.append({
                                    'cell_coordinates': (i, j),
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
    
    def transform_statement_to_question(self, statement: str, word: str, is_openai: bool = False) -> str:        
        """Given a statement with a word, where the word must be masked and we need to replace dot with questionmark at the end."""
        mask_string = "<mask>"
        masked_question = statement.replace(word, mask_string)[:-1] + "?"
        mask_count = masked_question.count(mask_string)
        if mask_count != 1:
            raise Exception("Multiple answer word found in the sentence.")
        
        if not is_openai:
            answer = self.unmasker(f"Kérdés: {masked_question}\nVálasz: {word}.")
            valid_token = self.has_question_candidates(answer)
            if valid_token:
                return masked_question.replace(mask_string, valid_token)[:-1] + "?"
            raise Exception(f"No valid solution found: {answer}")
        else:
            question = generate_question_from_sentence_openai(statement, word)
            return question
    
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
    
    def process_sections(self, sections: list[Section], logger, database):
        for section in sections:
            for index, table_section in enumerate(section.list_of_tables):
                results = self.find_matching_words(section.paragraph, table_section, strict=is_strict)
                for result in results:
                    row, col = result['cell_coordinates']
                    statement = result['matching_sentence'].lower().strip()
                    word = str(table_section.iat[row, col]).lower().strip()
                    try:
                        question = self.transform_statement_to_question(statement, word, is_openai=use_openai)
                        valid = True
                    except Exception as e:
                        logger.debug(e)
                        valid = False
                        question = "-"
                    logger.info(f"{section}(Szekció)\t{word}(Cella)\t{statement}(Mondat)\t{question}(Kérdés)\n{table_section}\n")
                    replaced_url = req.url.split("/")[-1].encode('ascii', 'replace').decode('ascii')
                    db_name = f'{replaced_url}_{section}_{index}'
                    database.generate_questions_table(db_name, table_section, [(question, word, valid, statement)], if_exists='append')

if __name__ == "__main__":
    use_openai = True
    is_strict = True
    data_path = "data/generated_hu.db"
    starting_page = "Szeged"
    log_path = 'data/wiki.log'
    page_count = 1
    
    database = Database(data_path)
    database.empty_database()
    logger: MyLogger = MyLogger(log_path=log_path, result_path=log_path)
    
    wikiyoinker = WikiYoinker(starting_page_name=starting_page)
    for x in range(page_count):
        req = wikiyoinker.get_next_page()
        sections = wikiyoinker.convert_url_to_section_data(req.url)
        wikiyoinker.process_sections(sections, logger, database)
    Report().create_report_from_db()