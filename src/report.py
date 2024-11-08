import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
import os
import sqlite3
from bs4 import BeautifulSoup
import shutil

class Report:
    def __init__(self, data_folder_path: str = "/home/gabortoth/Dokumentumok/Projects/QATesting/data") -> None:
        self.data_folder_path: str = data_folder_path
        self.speed_path: str = "speed_plot.png"
        self.accuracy_path: str = "accuracy_plot.png"
        self.report_remplate_path: str = "report_template.html"
        self.report_path: str = "report.html"
        self.db_path: str = f"{self.data_folder_path}/generated_hu.db"
        report_folder_path = os.path.join(data_folder_path, 'report')
        if os.path.exists(report_folder_path):
            shutil.rmtree(report_folder_path)
        os.makedirs(report_folder_path)    
    # Read the CSV file
    def read_csv(self, file_path):
        df = pd.read_csv(file_path, delimiter=';')
        df['Date'] = pd.to_datetime(df['Date'])  # Ensure Date column is datetime
        return df

    # Create plots
    def create_plots(self, df):
        plt.bar(df['Model name'], df['Accuracies'], color=['blue', 'green'])
        plt.title('Model Accuracies')
        plt.xlabel('Model name')
        plt.ylabel('Accuracy')
        accuracy_plot = '/home/p_tabtg/llama_project/QATesting/data/accuracy_plot.png'
        plt.savefig(accuracy_plot)
        plt.close()
        
        # Plot iteration speed over time
        plt.figure(figsize=(10, 6))
        plt.bar(df['Model name'], df['Iteration speed'], color=['blue', 'green'])
        plt.title('Model Accuracies')
        plt.xlabel('Model name')
        plt.ylabel('Iteration speed')

        speed_plot = '/home/p_tabtg/llama_project/QATesting/data/speed_plot.png'
        plt.savefig(speed_plot)
        plt.close()

        return accuracy_plot, speed_plot

    # Generate HTML report
    def generate_html_report(self, df, accuracy_plot, speed_plot, output_html):
        # Create the report content
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('/home/p_tabtg/llama_project/QATesting/data/report_template.html')
        
        # Render the template with the data
        html_content = template.render(data=df.to_dict(orient='records'), 
                                    accuracy_plot=accuracy_plot.split("/")[1],
                                    speed_plot=speed_plot.split("/")[1])
        
        # Write the HTML to a file
        with open(output_html, 'w') as f:
            f.write(html_content)

    def main(self):
        csv_file = '/home/p_tabtg/llama_project/QATesting/data/result.csv'  # Change this to your actual CSV file path
        output_html = '/home/p_tabtg/llama_project/QATesting/data/report.html'
        
        # Step 1: Read the CSV
        df = self.read_csv(csv_file)
        
        # Step 2: Create the plots
        accuracy_plot, speed_plot = self.create_plots(df)
        
        # Step 3: Generate HTML report
        self.generate_html_report(df, accuracy_plot, speed_plot, output_html)

        print(f"Report generated: {output_html}")
        
    def create_report_from_db(self):
        # Connect to SQLite Database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        print(self.db_path)

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
            df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
            
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
            with open(f"{self.data_folder_path}/report/{table_filename}", "w", encoding="utf-8") as file:
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
        with open(f"{self.data_folder_path}/report/index.html", "w", encoding="utf-8") as file:
            file.write(main_soup.prettify())

        # Close the connection
        conn.close()

                
if __name__ == '__main__':
    report = Report()
    report.create_report_from_db()
