# Hugging face API test
import requests
API_TOKEN = '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'
API_URL = "https://api-inference.huggingface.co/models/gpt2"
headers = {"Authorization": f"Bearer {API_TOKEN}"}
def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()
data = query("I am not having a great day.")
print(data)