from models import ModelLlama, pd, Database

if __name__ == "__main__":
    mydatabase2 = Database("data/fictional.db")
    mymodel = ModelLlama(url="https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-f16.gguf")

    df1 = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
        'Age': [25, 30, 35, 40, 28],
        'Occupation': ['Chef', 'Doctor', 'Artist', 'Lawyer', 'Agent'],
        'Salary': [70000, 120000, 50000, 90000, 95000]
    })
    columns = {
        'id': [],
        'utterance': [],
        'context': [],
        'targetValue': [],
    }  
    df = pd.DataFrame(columns)

    print(df1)
    print(mydatabase2.get_database_info())
    for x in range(30):
        # print(mydatabase2.get_question_with_table(x)[2][0] + "\t", mydatabase2.get_question_with_table(x)[1])
        # continue
        asd = mymodel.generate_question(df1.to_csv(index=False))

        new_row = {
            'id': f"nt-{x}",
            'utterance': asd[0],
            'context': "table",
            'targetValue': asd[1],
        }  
        df.loc[len(df)] = new_row
        print(new_row['targetValue']+"\t"+new_row['utterance'])
    mydatabase2.fill_database(df, "qa_table")
