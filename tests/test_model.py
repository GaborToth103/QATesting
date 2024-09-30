import sys
import os
sys.path.append(f"{os.getcwd()}/src")
import unittest
from utilities import measure_time, Suppressor
from llama_cpp import Llama

class TestCleanString(unittest.TestCase):
    with Suppressor():
        model = Llama(
            model_path="models/Llama-3.2-1B-Instruct-Q3_K_L.gguf",
            n_ctx=0,
            n_gpu_layers=-1,
        )

    def test_speed(self):    
        @measure_time
        def generating_things():
            with Suppressor():
                output = self.model(
                    "hello",
                    max_tokens=64,
                    echo=False,
                    stop=["<|", "<</", "[/INST]", "[INST]", "</s>", "\n", ". ", "</"],
                )
            return output["choices"][0]["text"].strip()
        
        print(generating_things()[0])
        self.assertTrue(generating_things()[1] < 1) # measured time is less than 1 second
            
if __name__ == '__main__':
    unittest.main()
