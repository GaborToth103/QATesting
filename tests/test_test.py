import sqlite3
import pandas as pd
from bs4 import BeautifulSoup

# Connect to SQLite Database
conn = sqlite3.connect('/home/gabortoth/Dokumentumok/Projects/QATesting/data/generated_hu.db')
cursor = conn.cursor()

# Retrieve all table names in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# List to store table names for the main index page
table_links = []

# Loop through each table and create an HTML page
for table_name_tuple in tables:
    table_name = table_name_tuple[0]
    table_filename = f"{table_name}.html"
    
    # Load the table into a DataFrame
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    
    # Convert DataFrame to HTML table
    html_table = df.to_html(index=False)

    # Use BeautifulSoup to structure the HTML document
    soup = BeautifulSoup("<html><head><title>{}</title></head><body></body></html>".format(table_name), "html.parser")
    
    # Add table name as header
    header = soup.new_tag("h1")
    header.string = f"Table: {table_name}"
    soup.body.append(header)
    
    # Insert the HTML table into the body
    table_soup = BeautifulSoup(html_table, "html.parser")
    soup.body.append(table_soup)
    
    # Write each table to a separate HTML file
    with open(f"/home/gabortoth/Dokumentumok/Projects/QATesting/data/report/{table_filename}", "w", encoding="utf-8") as file:
        file.write(soup.prettify())
    
    # Add a link to this table in the main index
    table_links.append((table_name, table_filename))

# Create the main index page
main_soup = BeautifulSoup("<html><head><title>Database Index</title></head><body></body></html>", "html.parser")

# Add a header for the main page
main_header = main_soup.new_tag("h1")
main_header.string = "Database Table Index"
main_soup.body.append(main_header)

# Create a list of links
for table_name, table_filename in table_links:
    link_tag = main_soup.new_tag("a", href=table_filename)
    link_tag.string = f"Table: {table_name}"
    main_soup.body.append(link_tag)
    
    # Add a line break after each link
    br_tag = main_soup.new_tag("br")
    main_soup.body.append(br_tag)

# Write the main index page to an HTML file
with open("/home/gabortoth/Dokumentumok/Projects/QATesting/data/report/index.html", "w", encoding="utf-8") as file:
    file.write(main_soup.prettify())

# Close the connection
conn.close()
