# HOST LOCAL AI USING OLLAMA

**Storage: Everything regarding this projetc is stored on the D: drive**

## Checkpoint 1: Audit the Legion’s exact hardware and software

### 1.GPU using  ```nvidia-smi```

```csv
name, memory.total [MiB], memory.used [MiB], memory.free [MiB], driver_version, temperature.gpu, power.draw [W], power.limit [W]
NVIDIA GeForce RTX 4060 Laptop GPU, 8188 MiB, 1048 MiB, 6910 MiB, 566.26, 39, 5.37 W, [N/A]
```

### 2.System's RAM using ```Get-CimInstance```

```txt
Manufacturer Model TotalRAM_GB
------------ ----- -----------
LENOVO       82WM        15.69

TotalRAM_GB FreeRAM_GB
----------- ----------
      15.69       6.41
```

### 3.System's disk size using ```Get-CimInstanc```

```txt
Name Used_GB Free_GB
---- ------- -------
C     163.05   36.07
D      28.17  723.47
```

### Checkpoint 2: Estimate usable model size based on hardware specs

Estimate disk size required to store the model: param * param_size (based on FP)

Splitting the model between VRAM and RAM:

* GPU VRAM: model layers + KV cache + buffers

* System RAM: remaining model layers + Ollama + Windows

Suggested model for simple first-time smoke test with minimal hardware tuning (i.e. place entirely on GPU VRAM): 1-3B models

### Checkpoint 3: Install and set up Ollama

Refer to their official website: https://docs.ollama.com/windows

Remember to configure OLLAMA_MODELS env variable to point the installation path for models into the directory you want with sufficient storage

### Checkpoint 4: Running the first model with Ollama

Use command ```ollama run <model_id>```. 

This command will: Check local model store --> Download model if absent --> Load model automatically to hardware --> launch an interactive chat session. 

The model used for the first smoke-test is ```qwen3.5:2b```

We see now why people say ollama is more user-friendly.

We can verify the hardware that ollama uses using ```nvidia-smi``` or ```ollama ps``` when the model is running.

```txt
NAME          ID              SIZE      PROCESSOR    CONTEXT    UNTIL
qwen3.5:2b    324d162be6ca    2.4 GB    100% GPU     4096       4 minutes from now

+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 566.26                 Driver Version: 566.26         CUDA Version: 12.7     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                  Driver-Model | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4060 ...  WDDM  |   00000000:01:00.0  On |                  N/A |
| N/A   48C    P4             57W /   60W |    4421MiB /   8188MiB |     90%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
```
