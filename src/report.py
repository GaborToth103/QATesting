import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
import os
import sqlite3

class Report:
    def __init__(self, data_folder_path: str = "data") -> None:
        self.data_folder_path: str = data_folder_path
        self.speed_path: str = "speed_plot.png"
        self.accuracy_path: str = "accuracy_plot.png"
        self.report_remplate_path: str = "report_template.html"
        self.report_path: str = "report.html"
        self.db_path: str = "generated_hu.db"
    
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
        """Create an HTML file in the data folder showing all tables in the SQLite database."""
        db_path = os.path.join(self.data_folder_path, self.db_path)
        
        # Ensure the data folder exists
        os.makedirs(self.data_folder_path, exist_ok=True)

        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Retrieve the list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Initialize HTML content
        html_content = "<html><head><title>Database Report</title></head><body>"
        html_content += "<h1>Database Report</h1>"

        # Loop through tables and create HTML tables for each
        for table_name in tables:
            table_name = table_name[0]  # Get the table name as a string
            html_content += f"<h2>Table: {table_name}</h2>"

            # Read the table into a DataFrame, using double quotes for the table name
            query = f'SELECT * FROM "{table_name}"'
            df = pd.read_sql_query(query, conn)
            html_content += df.to_html(index=False)  # Convert DataFrame to HTML

        # Close the database connection
        conn.close()

        # Complete the HTML content
        html_content += "</body></html>"

        # Write the HTML content to a file
        report_path = os.path.join(self.data_folder_path, "report.html")
        with open(report_path, "w") as file:
            file.write(html_content)

        print(f"Report created at {report_path}")
                
if __name__ == '__main__':
    report = Report()
    report.create_report_from_db()
