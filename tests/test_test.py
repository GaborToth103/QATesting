import sys
import os
sys.path.append(f"{os.getcwd()}/src")
from database import Database


db = Database("data/generated_hu.db")
qa_table = db.get_qa_table()
for index, row in qa_table.iterrows():
    statement = row['original']
    answer = row['targetValue']
    
