from llama_cpp import Llama

model = Llama(
    model_path="models/Meta-Llama-3-8B-Instruct.Q8_0.gguf",
    n_ctx=0,
    n_gpu_layers=-1,
)

output = model(
    "hello",
    max_tokens=None,
    echo=False,
    stop=["<|", "<</", "[/INST]", "[INST]", "</s>", "\n", ". "],
)
answer = output["choices"][0]["text"].strip()
print(answer)