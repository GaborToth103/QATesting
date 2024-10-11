import transformers
import torch

if __name__ == "__main__":
    llama = {"3.2/70": "meta-llama/Llama-3.1-70B-Instruct",
            "3.1/8": "meta-llama/Llama-3.1-8B-Instruct"}

    pipeline = transformers.pipeline(
        "text-generation",
        model=llama["3.1/8"],
        model_kwargs={"torch_dtype": torch.bfloat16,
                    "cache_dir": "/home/p_tabtg/p_tab_llm_scratch/.hfcache/hub"},
        device_map="auto",
        max_new_tokens = 32
    )
    answer = pipeline("Hey how are you doing today?")[0]["generated_text"]
    print(answer)