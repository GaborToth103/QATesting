import pandas as pd
import sqlite3

# Sample DataFrame
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['New York', 'Los Angeles', 'Chicago']
}
df = pd.DataFrame(data)

# Connect to SQLite database (it will create the database file if it doesn't exist)
conn = sqlite3.connect('example.db')

# Write the DataFrame to a SQL table
df.to_sql('people', conn, if_exists='replace', index=False)

# Close the connection
conn.close()
