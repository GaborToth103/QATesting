import unittest
import os
import urllib.request
from llama_cpp import Llama

class TestPreparation(unittest.TestCase):
    """Tests if the client is prepared to run the basics of the program like downloading or reaching certain modules."""
    
    url = "https://huggingface.co/lmstudio-community/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q8_0.gguf"
    name = url.split("/")[-1]
    folder_path = "models/"
    file_path = folder_path + name
    
    def test_testing(self):    
        self.assertTrue(True)
        
    def test_download_model(self):
        """test if it can download a model. It asserts true if the model is dowloaded successfully."""
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        if not os.path.isfile(self.file_path):
            print(f"Downloading model to {self.file_path} now.")
            urllib.request.urlretrieve(self.url, self.file_path)
            print(f"File downloaded successfully to {self.file_path}")
        self.assertTrue(True)

    def test_model_generation(self):    
        model = Llama(
            model_path=self.file_path,
            n_ctx=0,
            n_gpu_layers=-1,
        )
        
        output = model(
            "Hello ",
            max_tokens=64,
            echo=False,
            stop=["<|", "<</", "[/INST]", "[INST]", "</s>", "\n", "</"],
        )
        
        clean_output = output["choices"][0]["text"].strip()
        print(clean_output)
        self.assertTrue(clean_output)

if __name__ == '__main__':
    unittest.main()
