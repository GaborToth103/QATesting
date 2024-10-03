from models import ModelLlama, pd, Database

if __name__ == "__main__":
    mydatabase2 = Database("data/fictional.db")
    mymodel = ModelLlama(url="https://huggingface.co/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q8_0.gguf")


    df1 = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Erika'],
        'Age': [25, 30, 35, 40, 28],
        'Occupation': ['Chef', 'Doctor', 'Artist', 'Lawyer', 'Agent'],
        'Salary': ["$70k", "$120k", "$50k", "$90k", "$95k"]
    })
    df1 = pd.DataFrame({
        'Név': ['Alice', 'Bob', 'Charlie', 'David', 'Erika'],
        'Életkor': [25, 30, 35, 40, 28],
        'Foglalkozás': ['Séf', 'Orvos', 'Művész', 'Ügyvéd', 'Ügynök'],
        'Jövedelem': ["$70k", "$120k", "$50k", "$90k", "$95k"]
    })
    columns = {
        'id': [],
        'utterance': [],
        'context': [],
        'targetValue': [],
    }  
    df = pd.DataFrame(columns)
    print(df1, "\nNumber of questions in the datatable is", mydatabase2.get_database_info(), "\n")
    for x in range(30):
        # print(mydatabase2.get_question_with_table(x)[2][0] + "\t", mydatabase2.get_question_with_table(x)[1])
        # continue
        asd = mymodel.generate_question(df1.to_csv(index=False), False)

        new_row = {
            'id': f"nt-{x}",
            'utterance': asd[0],
            'context': "table",
            'targetValue': asd[1],
        }  
        df.loc[len(df)] = new_row
        print(f"{x}\t{new_row['targetValue']}\t{new_row['utterance']}")
    mydatabase2.fill_database(df, "qa_table")

