from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("togethercomputer/LLaMA-2-7B-32K")
model = AutoModelForCausalLM.from_pretrained("togethercomputer/LLaMA-2-7B-32K", trust_remote_code=True, torch_dtype=torch.float16)

input_context = "<|user|>\How many planets are there?</s>\n<|assistant|>"
input_ids = tokenizer.encode(input_context, return_tensors="pt")
output = model.generate(input_ids, max_length=30, temperature=0.7)
output_text = tokenizer.decode(output[0], skip_special_tokens=True)
print(output_text)
