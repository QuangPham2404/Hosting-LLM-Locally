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

## Checkpoint 2: Estimate usable model size based on hardware specs

Estimate disk size required to store the model: param * param_size (based on FP)

Splitting the model between VRAM and RAM:

* GPU VRAM: model layers + KV cache + buffers

* System RAM: remaining model layers + Ollama + Windows

Suggested model for simple first-time smoke test with minimal hardware tuning (i.e. place entirely on GPU VRAM): 1-3B models

## Checkpoint 3: Install and set up Ollama

Refer to their official website: https://docs.ollama.com/windows

Remember to configure OLLAMA_MODELS env variable to point the installation path for models into the directory you want with sufficient storage

## Checkpoint 4: Running the first model with Ollama

Use command ```ollama run <model_id>```. 

This command will: Check local model store --> Download model if absent --> Load model automatically to hardware --> launch an interactive chat session. 

The model used for the first smoke-test is ```qwen3.5:2b```

We see now why people say ollama is more user-friendly.

## Check point 5: Checking hardware usage when model is running

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

## Check point 6: Understanding what ollama loads when we install a model

#### You can see the model's meta-data using ```ollama show <model_name> --<parameter [optional]>```

```txt
Model
    architecture        qwen35
    parameters          2.3B
    context length      262144
    embedding length    2048
    quantization        Q8_0
    requires            0.17.1

  Capabilities
    completion
    vision
    tools
    thinking

  Parameters
    top_p               0.95
    presence_penalty    1.5
    temperature         1
    top_k               20

  License
    Apache License
    Version 2.0, January 2004
    ...
```
#### What ollama loads with a model:

* The ```blob``` directory: This directory holds the key data of the models (model weights, configuration data, etc) in files. You will see that these files have *content-addressed storage*

```txt
OLLAMA_MODELS
└── blobs
    ├── sha256-abc123...
    ├── sha256-def456...
    └── sha256-ghi789...
```

* The ```manifest``` directory: This directory contains small files that have meta-data of models. The file itself is usually JSON.

```txt
manifests
└── registry.ollama.ai
    └── library
        └── qwen3.5
            └── 2b

# What a file will look like in JSON
{
  "config": {
    "digest": "sha256:..."
  },
  "layers": [
    {
      "digest": "sha256:...",
      "size": 2700000000
    }
  ]
}
```

* An analogy of the ```blobs``` and ```manifest``` directory will be the former to be the actual files while the latter being the table of content. 

#### What is loaded to the hardware when the model is launched

A good estimation will be: TOTAL = model files + KV Cache + Other buffers (compute, overhead, etc).

This means the disk size of the model indicated by Ollama on the model database is SMALLER than the actuall size you need for the VRAM + RAM when it is launched locally.

## Check point 7: Understand model lifecycle and runtime controls

#### The model life-cycle

Simply put, when unloaded, the model resides fully on the hard disk. When loaded, it is loaded to the hardware (RAM, VRAM, etc). When we're done, Ollama will keep the model "alive" for around an extra 5 minutes until unloading it from the hardware.

To completely turn off Olama, use manual toggle from the Ollama icon in the bottom-left panel on windows.

#### Runtime controls

**Where we can change the controls**

| Where to set the vars | How do you set it | Where it is applied |
| --- | --- | --- |
Interactive sessions | Using the command ```/set``` directly in the chat session | In the current running chat session, will not retain for future sessions
*API Request* | Set in the JSON request sent to the model API | Applied only for that specified prompt
*Modelfile* | Using a manually create modelfile, which will allow you to create a "custom" model based on ollama with specified configuration, persona, etc. The command is ```ollama create <custom_model_name> -f .\<Modelfile_path>``` then ```ollama run <custom_model_name>``` | Applied whenever you run that custom model
Environment var | Setting Ollama environmental variables such as ```OLLAMA_MODEL``` similar how you set OLLAMA_MODEL | Applied to ALL instances ran with Ollama

**What the runtime controls are**

| Control | Simple meaning | Chat session | API request | Modelfile | Ollama environment variable |
|---|---|:---:|:---:|:---:|:---:|
| `temperature` | The creatvity dial. Higher means more "adventerous", good for brainstorming, poetry, etc. Lower means more "conversative", good for maths, coding, etc. | Yes, if supported by `/set parameter` | Yes, under `options` | Yes, with `PARAMETER` | No |
| `top_k` | Before picking the next word, the model ranks candidates by likelihood. top_k says "only consider the top K options." | Yes, if supported | Yes, under `options` | Yes, with `PARAMETER` | No |
| `top_p` | Instead of a fixed number of words like top_k, this says "keep adding candidate words until their combined probability reaches P%." | Yes, if supported | Yes, under `options` | Yes, with `PARAMETER` | No |
| `min_p` | Removes tokens whose probability is too small relative to the most likely token. | Yes, if supported | Yes, under `options` | Yes, with `PARAMETER` | No |
| `seed` | Sets the random-number seed (like in randint for C). A fixed seed helps make repeated tests more reproducible. | Yes, if supported | Yes, under `options` | Yes, with `PARAMETER` | No |
| `num_ctx` | Sets the context-window allocation: how many tokens the model can keep available at once. Larger values require more memory. | Yes, if supported | Yes, under `options` | Yes, with `PARAMETER` | `OLLAMA_CONTEXT_LENGTH` can set a server default |
| `num_predict` | Limits the maximum number of new tokens the model may generate. | Yes, if supported | Yes, under `options` | Yes, with `PARAMETER` | No |
| `repeat_last_n` | Sets how many recent tokens Ollama checks when looking for repetition ("have I said this before?"). | Yes, if supported | Yes, under `options` | Yes, with `PARAMETER` | No |
| `repeat_penalty` | Discourages repeated words or token sequences. Excessively high values can make writing unnatural. | Yes, if supported | Yes, under `options` | Yes, with `PARAMETER` | No |
| `stop` | Stops generation when a specified text sequence is produced. | Yes, if supported | Yes, under `options` | Yes, with `PARAMETER` | No |
| System message | Gives the model high-level instructions, such as its role, tone, or task. It becomes part of the prompt. | Yes, using `/set system` if supported | Yes, using a `system` message in `messages` | Yes, with `SYSTEM` | No |
| Prompt template | Defines how system, user, and assistant messages are formatted before tokenization. Normally model-specific. | No | Usually not changed per normal chat request | Yes, with `TEMPLATE` | No |
| `keep_alive` | Controls how long the model remains loaded in RAM or VRAM after a request. | Not normally set inside chat | Yes, as a top-level request field | No | `OLLAMA_KEEP_ALIVE` |
| Model storage path | Controls where downloaded model files are stored. | No | No | No | `OLLAMA_MODELS` |
| Server host and port | Controls which network address Ollama listens on. | No | No | No | `OLLAMA_HOST` |