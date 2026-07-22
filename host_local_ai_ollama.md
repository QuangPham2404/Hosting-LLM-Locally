# HOST LOCAL AI USING OLLAMA

**Storage: Everything regarding this projetc is stored on the D: drive**

**Where to type commands: Open Git Bash, this allow you to use similar syntax to Linux environment rather than spending time debugging the powershell syntax**

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

### How hosting a local model server with Ollama works:

1. Install Ollama on your local machine (it's a lightweight server application).
2. Pull a model using ollama pull <model-name> (e.g., ollama pull llama3.1 or ollama pull mistral). This downloads the model weights to your machine — this is the "installing the model" step you mentioned.
3. Ollama runs a local server (by default at http://localhost:11434) that exposes a REST API you can hit for things like /api/generate, /api/chat, /api/embeddings, etc.
4. You can then interact with the model either through:
   * The CLI directly (ollama run llama3.1)
   * The REST API (via curl, Python requests, etc.)
   * Client libraries (Ollama has official Python and JS libraries)
   * Many third-party apps and frameworks (like LangChain, LlamaIndex, Open WebUI) that support Ollama as a backend

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

### You can see the model's meta-data using ```ollama show <model_name> --<parameter [optional]>```

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
### What ollama loads with a model:

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

### What is loaded to the hardware when the model is launched

A good estimation will be: TOTAL = model files + KV Cache + Other buffers (compute, overhead, etc).

This means the disk size of the model indicated by Ollama on the model database is SMALLER than the actuall size you need for the VRAM + RAM when it is launched locally.

## Check point 7: Understand model lifecycle and runtime controls

### The model life-cycle

Simply put, when unloaded, the model resides fully on the hard disk. When loaded, it is loaded to the hardware (RAM, VRAM, etc). When we're done, Ollama will keep the model "alive" for around an extra 5 minutes until unloading it from the hardware.

To completely turn off Olama, use manual toggle from the Ollama icon in the bottom-left panel on windows.

### Runtime controls

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

## Check point 8: Using Ollama as a model server

### Some definitions

1. **API - Application Programming Interface**: is a communcation interface (a "messenger" in simple terms) that allows users to send JSON request to the model server how they can recieve responses from the model itself
2. **API endpoint**: The model server will host an API Endpoint, which is an URL, where the server will listen for request for processing and return a response. For Ollama, the default endpoint is ```http://localhost:11434```.  A note: this same endpoint is used for Ollama on the same computer, meaning all models will use it - you need to specify the model during the request so that Ollama can load the correct model to process the request.

### Using Ollama by direct API vs CLI

* **CLI**: You send your prompt via Ollama's command line directly on your computer. The model is started in this method using: ```ollama run <model_name>```
* **Direct API**: The model receives the prompt via JSON request using ```curl```. Note if the the Ollama server is started (else start it with ```ollama serve```), you DO NOT need the command ```ollama run <model_name>``` - just remeber specifying the model in the JSON request.

A note: When you run Ollama on your computer, it uses YOUR hardware to host and model server and the CLI and direct API method are both CLIENTS of the that server! The whole flow of the 2 methods are shown below. The cleanest mental model of how Ollama works is: *Ollama server owns and runs the model. Clients communicate with the server and request inference.*

```txt
# The CLI method
You type into terminal
        ↓
Ollama CLI client
        ↓ request
Ollama server
        ↓
qwen3.5:2b on GPU
        ↓ response
Ollama CLI prints the answer

# The direct API method
You construct JSON
        ↓
curl HTTP client
        ↓ HTTP request
Ollama server
        ↓
qwen3.5:2b on GPU
        ↓ JSON response
curl prints the response
```

### More about using the direct API method

Find more info at the offiical Ollama API guide: https://docs.ollama.com/api

Example API request:

```txt
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3.5:2b",
  "prompt": "Why is the sky blue?",
  "options": {
    "temperature": 0.8,
    "top_p": 0.9,
    "seed": 42
  }
}'
```

The response will be pasted on the terminal, you might need some JSON parsing to make it more readable.

### Ollama API provides a lot of end points with different usage cases.

Ollama starts a local HTTP API server at:

`http://localhost:11434/api`

The examples below use `gemma3` as the model name. Replace it with the model you have installed, such as `qwen3.5:2b`.

| HTTP Method | Endpoint | Simple explanation | Example |
|---|---|---|---|
| `POST` | `/api/generate` | Sends a single prompt to a model and generates a response. Best for simple, one-shot prompts where you manage the prompt yourself. | `curl http://localhost:11434/api/generate -d '{"model":"gemma3","prompt":"Explain what VRAM is in simple terms.","stream":false}'` |
| `POST` | `/api/chat` | Sends a conversation as a list of messages. Best for chatbots, agents, and multi-turn conversations because messages have roles such as `system`, `user`, and `assistant`. | `curl http://localhost:11434/api/chat -d '{"model":"gemma3","messages":[{"role":"user","content":"Explain what VRAM is in simple terms."}],"stream":false}'` |
| `POST` | `/api/embed` | Converts text into numerical vectors called embeddings. Used for semantic search, document retrieval, similarity comparison, and RAG systems. Requires an embedding model. | `curl http://localhost:11434/api/embed -d '{"model":"embeddinggemma","input":"GPU memory bandwidth is important for AI workloads."}'` |
| `GET` | `/api/tags` | Lists all models currently downloaded and stored by Ollama. Similar to running `ollama list`. | `curl http://localhost:11434/api/tags` |
| `GET` | `/api/ps` | Lists models currently loaded into RAM or VRAM and available for inference. Similar to running `ollama ps`. | `curl http://localhost:11434/api/ps` |
| `POST` | `/api/show` | Displays detailed information about a model, including its architecture, parameter size, quantization, template, system prompt, parameters, and capabilities. | `curl http://localhost:11434/api/show -d '{"model":"gemma3"}'` |
| `POST` | `/api/create` | Creates a customized Ollama model from an existing model. You can embed a system prompt, template, parameters, message history, or quantization settings. This is the API equivalent of building a model from a `Modelfile`. | `curl http://localhost:11434/api/create -d '{"model":"study-assistant","from":"gemma3","system":"You are a concise engineering study assistant.","parameters":{"temperature":0.3},"stream":false}'` |
| `POST` | `/api/copy` | Creates another model name that points to a copy of an existing local model. Useful before experimenting with a model configuration or giving it a clearer name. | `curl http://localhost:11434/api/copy -d '{"source":"gemma3","destination":"gemma3-backup"}'` |
| `POST` | `/api/pull` | Downloads a model from the Ollama model registry. Similar to running `ollama pull gemma3`. | `curl http://localhost:11434/api/pull -d '{"model":"gemma3","stream":false}'` |
| `POST` | `/api/push` | Uploads a model to the Ollama registry under your Ollama account. The model normally needs a namespaced name such as `username/model-name`, and you must be signed in. | `curl http://localhost:11434/api/push -d '{"model":"your-username/study-assistant","stream":false}'` |
| `DELETE` | `/api/delete` | Permanently removes a downloaded model from local storage. Similar to running `ollama rm gemma3`. | `curl -X DELETE http://localhost:11434/api/delete -d '{"model":"gemma3-backup"}'` |
| `GET` | `/api/version` | Returns the version of the currently running Ollama server. Useful for troubleshooting and compatibility checks. | `curl http://localhost:11434/api/version` |

### The Most Important Distinction: Generate vs Chat

| Endpoint | Input format | Best used for |
|---|---|---|
| `/api/generate` | One main `prompt` string | One-shot generation, completion, testing prompts, or applications that construct their own prompt format |
| `/api/chat` | A `messages` array containing roles and message content | Chat applications, agents, system instructions, and multi-turn conversation history |

For the "chat" endpoints, your request must include the conversation history, since Ollama will NOT save it. Below is an example of a multi-step conversation:

```txt
# First message from user
curl http://localhost:11434/api/chat \
  -d '{
    "model": "qwen3.5:2b",
    "messages": [
      {
        "role": "user",
        "content": "My name is Quang."
      }
    ],
    "stream": false
  }'

{
  "message": {
    "role": "assistant",
    "content": "Nice to meet you, Quang."
  }
}


# First response from model server
{
  "message": {
    "role": "assistant",
    "content": "That is a broad field covering electronics, power, control, and many other areas."
  }
}


# Second message from user, saving the previous request and response
curl http://localhost:11434/api/chat \
  -d '{
    "model": "qwen3.5:2b",
    "messages": [
      {
        "role": "user",
        "content": "My name is Quang."
      },
      {
        "role": "assistant",
        "content": "Nice to meet you, Quang."
      },
      {
        "role": "user",
        "content": "I study electrical engineering."
      }
    ],
    "stream": false
  }'
```

In order to parse and save the reponse and request automatically, we can use a Python script or something similar.

### Streaming

Streaming means the model will "paste" token as it generates. In contrast, no streaming means waiting until the whole response is generated and only then it is shown to the user.

The following endpoints stream their output by default:

- `/api/generate`
- `/api/chat`
- `/api/create`
- `/api/pull`
- `/api/push`

Add the following field to receive one final JSON response instead:

`"stream": false`

Example:

`curl http://localhost:11434/api/generate -d '{"model":"gemma3","prompt":"Hello","stream":false}'`

Streaming is useful for interactive applications because tokens or progress updates appear as soon as they are available.

### Common CLI and API Equivalents

A note is that the ```ollama run``` command will automatically install the model if it is note present. However, the ```api/generate``` and ```api/chat``` will NOT - the installation is dones using the ```/api/pull``` request. So best to just install manually the model using CLI first before setting up the model server later using the direct API method.

| Ollama CLI command | Approximate API equivalent |
|---|---|
| `ollama run gemma3` | `POST /api/generate` or `POST /api/chat` |
| `ollama list` | `GET /api/tags` |
| `ollama ps` | `GET /api/ps` |
| `ollama show gemma3` | `POST /api/show` |
| `ollama create my-model` | `POST /api/create` |
| `ollama cp gemma3 my-model` | `POST /api/copy` |
| `ollama pull gemma3` | `POST /api/pull` |
| `ollama push username/my-model` | `POST /api/push` |
| `ollama rm gemma3` | `DELETE /api/delete` |
| `ollama --version` | `GET /api/version` |

## Check point 9: Hosting a minimal client using Ollama