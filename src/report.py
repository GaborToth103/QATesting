import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader

class Report:
    def __init__(self, data_folder_path: str = "data") -> None:
        self.data_folder_path: str = data_folder_path
        self.speed_path: str = "speed_plot.png"
        self.accuracy_path: str = "accuracy_plot.png"
        self.report_remplate_path: str = "report_template.html"
        self.report_path: str = "report.html"
    
    # Read the CSV file
    def read_csv(file_path):
        df = pd.read_csv(file_path, delimiter=';')
        df['Date'] = pd.to_datetime(df['Date'])  # Ensure Date column is datetime
        return df

    # Create plots
    def create_plots(df):
        plt.bar(df['Model name'], df['Accuracies'], color=['blue', 'green'])
        plt.title('Model Accuracies')
        plt.xlabel('Model name')
        plt.ylabel('Accuracy')
        accuracy_plot = 'data/accuracy_plot.png'
        plt.savefig(accuracy_plot)
        plt.close()
        
        # Plot iteration speed over time
        plt.figure(figsize=(10, 6))
        plt.bar(df['Model name'], df['Iteration speed'], color=['blue', 'green'])
        plt.title('Model Accuracies')
        plt.xlabel('Model name')
        plt.ylabel('Iteration speed')

        speed_plot = 'data/speed_plot.png'
        plt.savefig(speed_plot)
        plt.close()

        return accuracy_plot, speed_plot

    # Generate HTML report
    def generate_html_report(df, accuracy_plot, speed_plot, output_html):
        # Create the report content
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('data/report_template.html')
        
        # Render the template with the data
        html_content = template.render(data=df.to_dict(orient='records'), 
                                    accuracy_plot=accuracy_plot.split("/")[1],
                                    speed_plot=speed_plot.split("/")[1])
        
        # Write the HTML to a file
        with open(output_html, 'w') as f:
            f.write(html_content)

    def main():
        csv_file = 'data/result.csv'  # Change this to your actual CSV file path
        output_html = 'data/report.html'
        
        # Step 1: Read the CSV
        df = read_csv(csv_file)
        
        # Step 2: Create the plots
        accuracy_plot, speed_plot = create_plots(df)
        
        # Step 3: Generate HTML report
        generate_html_report(df, accuracy_plot, speed_plot, output_html)

        print(f"Report generated: {output_html}")

if __name__ == '__main__':
    main()
