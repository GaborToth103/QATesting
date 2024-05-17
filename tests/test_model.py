from llama_cpp import Llama
import sys
import os
sys.path.append(f"{os.getcwd()}/src")
from utilities import measure_time

class TestFunction():
    model = Llama(
        model_path="models/Meta-Llama-3-8B-Instruct.Q8_0.gguf",
        n_ctx=0,
        n_gpu_layers=-1,
    )

    def test_speed(self):    
        @measure_time
        def generating_things():
            output = self.model(
                "hello",
                max_tokens=64,
                echo=False,
                stop=["<|", "<</", "[/INST]", "[INST]", "</s>", "\n", ". "],
            )
            return output["choices"][0]["text"].strip()
        
        assert generating_things()[1] < 1 # measured time is less than 1 second
            

if __name__ == "__main__":    
    TestFunction().test_speed()