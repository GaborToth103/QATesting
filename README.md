# Table Question Answering Evaluation
Frist, copy the generated database and model list files to the data/ folder.
Run requirements.txt and use the main.py script to run evaluation Framework.
Run wikipediaYouinker.py to run Wikipedia webscaper.

## Important
Use this to make sure CUDA is enabled, otherwise only the CPU will be used if llama_cpp architecture is the main goal:
```
CMAKE_ARGS="-DLLAMA_CUBLAS=on -DCMAKE_CUDA_ARCHITECTURES=all-major" FORCE_CMAKE=1 pip install llama-cpp-python --no-cache-dir --force-reinstall --upgrade
```
To check GPU state:
```
nvidia-smi
```