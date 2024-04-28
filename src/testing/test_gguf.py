# CMAKE_ARGS="-DLLAMA_CUBLAS=on -DCMAKE_CUDA_ARCHITECTURES=all-major" FORCE_CMAKE=1 pip install llama-cpp-python --no-cache-dir --force-reinstall --upgrade
import os
import urllib.request
from llama_cpp import Llama
import decorators

def download_file(url: str, folder_path: str) -> str:
    """Dowloading GGUF model from HuggingFace, checks if the file already exists before downloading.

    Args:
        url (str): URL to the HuggingFace gguf file.
        folder_path (str): The relative or absolute folder path.

    Returns:
        str: The absolute local file path.
    """
    file_path = folder_path + url.split("/")[-1]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    if not os.path.isfile(file_path):
        decorators.logging.info(f"Downloading model to {file_path} now.")
        urllib.request.urlretrieve(url, file_path)
        decorators.logging.info(f"File downloaded successfully to {file_path}")
    return file_path

@decorators.measure_time
def model_answer(local_path: str, prompt: str) -> str:
    try:
        llm = Llama(local_path, n_gpu_layers= -1)
        output = llm(prompt, max_tokens=512, stop=["<|"])
        return output["choices"][0]["text"].strip()
    except Exception as e:
        return e

def main():
    folder_path = "models/"
    prompt = f"""<|im_start|>system
    You are an assistant that briefly answers the user's questions.<|im_end|>
    <|im_start|>user
    How many planets are there in our Solar System? Write only the correct number!<|im_end|>
    <|im_start|>assistant
    """
    with open('data/model_list.txt', 'r') as file:
        model_urls = file.readlines()
    for index, model_url in enumerate(model_urls):
        file_path = download_file(model_url.strip(), folder_path)
        answer = model_answer(file_path, prompt)

if __name__ == "__main__":
    main()