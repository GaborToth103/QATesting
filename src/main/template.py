# pip install llama-cpp-python
import os
import urllib.request
from llama_cpp import Llama

def download_file(url, path):
    # Dowloading GGUF model from HuggingFace, checks if the file already exists before downloading
    path = path + url.split("/")[-1]
    if not os.path.isfile(path):
        print("Downloading model...")
        urllib.request.urlretrieve(url, path)
        print("File downloaded successfully.")
    else:
        print("File already exists.")
    return path

def get_llm(path, context_length = 512, gpu_layers = -1, cpu_threads=None):
    # Creates a Llama object
    llm = Llama(
        model_path=path,
        n_ctx=context_length, # context length to feed the model, the larger context length significantly increases time cost
        n_threads=cpu_threads, # maximum number of cpu threads to use
        n_gpu_layers=gpu_layers, # gpu layers to use if acceleration is available
    )
    return llm

def generate_text(llm, prompt, max_tokens=512, temperature=0.1, top_p=0.5, echo=False, stop=["#", "User:", "<|im_end|>"]):
    # Generates text from the prompt provided
    output = llm(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        echo=echo,
        stop=stop,
    )
    return output["choices"][0]["text"].strip()

path = "models/" # path to store model files
example_model = "https://huggingface.co/NousResearch/Hermes-2-Pro-Mistral-7B-GGUF/resolve/main/Hermes-2-Pro-Mistral-7B.Q4_K_M.gguf"
example_model_small = "https://huggingface.co/MaziyarPanahi/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/TinyLlama-1.1B-Chat-v1.0.Q2_K.gguf"
example_model_large = "https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF/resolve/main/mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf"
prompt = f"""<|im_start|>system
You are an assistant that briefly answers the user's questions.<|im_end|>
<|im_start|>user
How many planets are there in our Solar System?<|im_end|>"""
prompt2 = f"[INST] How many planets are there in our Solar System? [/INST]"
path = download_file(example_model_large, path)
llm = get_llm(path)
output = generate_text(llm, prompt2)
print(output) # The Solar System consists of 8 planets, including Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. These planets orbit around the Sun, which is at the center of our solar system.