# Local AI Model Hosting Learning Plan

## Project Goal

Build a strong foundation in local AI model hosting on a Lenovo Legion 5 Pro 2023 R9000P with an NVIDIA GeForce RTX 4060 Laptop GPU.

The learning sequence is intentionally divided into:

1. Core hosting fundamentals
2. Larger-model deployment
3. Hardware-aware optimization
4. Lower-level inference tooling

---

## Phase 1 — Hardware and Environment Audit

### Checkpoint 1: Audit the Legion’s Exact Hardware and Software

Key points:

- Confirm the exact GPU model and available VRAM.
- Check NVIDIA driver status and GPU visibility.
- Inspect total and currently available system RAM.
- Check available disk space and choose where model files should be stored.
- Decide whether to use native Windows or WSL for the initial workflow.

### Checkpoint 2: Estimate Usable Model Size Based on Hardware Specs

Key points:

- Relate model parameter count and numerical precision to memory usage.
- Understand that model file size is not equal to total runtime VRAM use.
- Account for model weights, KV cache, runtime buffers, and OS GPU usage.
- Identify a safe first model size and a realistic larger-model target.

---

## Phase 2 — Ollama Setup and First Model

### Checkpoint 3: Install and Set Up Ollama

Key points:

- Install Ollama natively on Windows.
- Verify the executable location and installed version.
- Configure the model storage directory on the larger secondary drive.
- Confirm that Ollama inherits the correct environment variables.
- Verify that downloaded models are actually stored in the intended directory.

### Checkpoint 4: Run the First Model with Ollama

Key points:

- Download and run a small local instruction-tuned model.
- Confirm that the model responds correctly through the Ollama CLI.
- Verify that inference runs fully on the RTX 4060 GPU.
- Learn the basic model lifecycle: download, load, run, stop, and unload.
- Establish a known-working baseline before making any tuning changes.

---

## Phase 3 — Essential Model-Hosting Skills

### Checkpoint 5: Measure the Baseline

Key points:

- Record model size, VRAM use, system RAM use, context allocation, and GPU activity.
- Observe idle versus active GPU behavior.
- Note approximate response speed, temperature, and power draw.
- Create a reference point for later comparisons.

### Checkpoint 6: Understand the Model Package

Key points:

- Understand model names, tags, manifests, and content-addressed blobs.
- Identify the model family, parameter count, and quantization format.
- Distinguish between parameter count, disk size, and runtime memory use.
- Understand how Ollama maps a friendly model name to the underlying files.

### Checkpoint 7: Understand Model Lifecycle and Runtime Controls

Key points:

- Learn how Ollama manages models on disk, in RAM, and in VRAM.
- Understand the purpose of context length, temperature, top-p, output limits, and keep-alive.
- Separate memory controls, generation controls, prompt controls, and lifecycle controls.
- Use Ollama commands to inspect, run, show, stop, and list models.

### Checkpoint 8: Use Ollama as a Model Server

Key points:

- Understand the difference between the Ollama CLI and the Ollama server.
- Learn how a client communicates with the local server using HTTP and JSON.
- Understand localhost, port 11434, request payloads, and response formats.
- Compare streamed and non-streamed generation.
- Recognize that the server owns the model and GPU resources.

### Checkpoint 9: Build a Minimal Client

Key points:

- Write a small PowerShell or Python client.
- Send prompts to the Ollama API.
- Receive and display streamed responses.
- Handle basic connection and response errors.
- Understand the boundary between client application, model server, inference runtime, and GPU.

---

## Phase 4 — Larger Models and Hardware-Aware Optimization

### Checkpoint 10: Host a Larger Model

Key points:

- Select a larger quantized instruction model that is suitable for the RTX 4060.
- Reuse the same Ollama server and client workflow.
- Observe model loading time, GPU residency, CPU offloading, and memory pressure.
- Compare practical capability against the smaller baseline model.

### Checkpoint 11: Compare Small and Large Models

Key points:

- Use the same prompts, context length, and client.
- Compare answer quality, latency, throughput, VRAM use, and system RAM use.
- Keep variables controlled so the model size is the main difference.
- Record results in a structured comparison.

### Checkpoint 12: Identify Memory and Performance Bottlenecks

Key points:

- Determine whether the main limit is VRAM capacity, memory bandwidth, CPU offload, PCIe traffic, or thermals.
- Separate prompt-processing performance from token-generation performance.
- Observe how context length and concurrent requests affect memory.
- Form hypotheses before changing settings.

### Checkpoint 13: Optimize Systematically

Key points:

- Change one variable at a time.
- Test model size, quantization, context length, batch size, and concurrency.
- Measure time to first token, prompt throughput, generation throughput, VRAM use, power, and temperature.
- Keep a reproducible experiment log.
- Apply an HPC-style workflow: baseline, bottleneck, hypothesis, experiment, measurement, and explanation.

### Checkpoint 14: Reproduce the Workflow with `llama.cpp`

Key points:

- Move from Ollama’s high-level abstraction to a lower-level inference engine.
- Work directly with GGUF model files.
- Control GPU offloading, context size, batch size, and server parameters.
- Compare `llama.cpp` behavior and performance against Ollama.
- Use this stage to understand what Ollama previously handled automatically.

---

## Overall Progression

```text
Audit hardware
→ estimate feasible model sizes
→ install and configure Ollama
→ run a first model
→ understand the model package
→ understand runtime controls
→ use the API
→ build a client
→ host a larger model
→ identify bottlenecks
→ optimize systematically
→ repeat with llama.cpp
```

The objective is to first master reliable model hosting, then move into performance engineering and hardware-aware optimization.
