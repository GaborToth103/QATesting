# QATesting
Initial release. Run requirements.txt and use the main.py script to run.

# Important
Use this to make sure CUDA is enabled, otherwise only the CPU will be used:
```
CMAKE_ARGS="-DLLAMA_CUBLAS=on -DCMAKE_CUDA_ARCHITECTURES=all-major" FORCE_CMAKE=1 pip install llama-cpp-python --no-cache-dir --force-reinstall --upgrade
```

To check GPU state:
```
nvidia-smi
```

# TODO
- prompt
- log