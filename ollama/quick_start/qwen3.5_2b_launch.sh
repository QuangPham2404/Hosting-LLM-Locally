#!/usr/bin/env bash

# This is the script for quick-start qwen3.5:2b model with Ollama. This will download the model if not installed and then start a local chat with the model

# Pre-req: Ollama is installed and the OLLAMA_MODEL environment variable is set up

# We should add ollama exe PATH to the PATH environment variable so that when the script runs, bash can find the ollama command
# export PATH="$PATH:/C:/Users/STVN/AppData/Local/Programs/Ollama"

# This script proves the easy-to-use feature of Ollama

ollama run qwen3.5:2b