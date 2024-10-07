import pandas as pd
import requests
from bs4 import BeautifulSoup

# Define the Wikipedia URL
url = "https://en.wikipedia.org/wiki/Szeged"

# Send a GET request to fetch the page content
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find all tables in the Wikipedia page
tables = soup.find_all('table', {'class': 'wikitable'})

# Extract the first table using pandas

df = pd.read_html(str(tables))

# Show the extracted table data
print(df)
