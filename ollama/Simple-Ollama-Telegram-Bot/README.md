# Local Ollama Telegram Bot

This project connects a Telegram bot to a language model running locally through Ollama.

The Python application receives Telegram messages, sends them to the local Ollama HTTP API, receives the generated response, and sends that response back to Telegram.

```text
Telegram user
    -> Telegram bot
    -> Python application
    -> Ollama at localhost:11434
    -> Local model
    -> Telegram response
```

The project is being developed as a learning exercise, one layer at a time. It currently supports one active conversation in memory.

## Requirements

- Windows with PowerShell.
- Python 3.9 or newer.
- Ollama installed and running.
- A locally available Ollama model.
- A Telegram bot token created through BotFather.
- VS Code or another Python-capable editor.

The current model configuration is stored in `ollama_client.py`:

```python
MODEL_NAME = "qwen3.5:2b"
```

Change this value to the name of another model installed in Ollama if needed.

## Project Setup

Open a PowerShell terminal in this directory.

Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
python -m pip install --upgrade pip
python -m pip install python-telegram-bot python-dotenv
```

Create a file named `.env` in the project root:

```text
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

The token is loaded at runtime by `telegram_echo_bot.py`. It is not stored in the Python source code.

Do not commit `.env`, `.venv`, or `__pycache__` to Git. Add them to `.gitignore` before committing the project.

## Starting the Bot

Make sure Ollama is running and the configured model is available:

```powershell
ollama list
```

From a new VS Code terminal, activate the virtual environment and start the bot:

```powershell
.\.venv\Scripts\Activate.ps1
python .\telegram_echo_bot.py
```

The bot must remain running in the VS Code terminal while you use it from Telegram. Closing the terminal or pressing `Ctrl+C` stops the bot.

The virtual environment can also be used without activation:

```powershell
.\.venv\Scripts\python.exe .\telegram_echo_bot.py
```

The dependencies only need to be installed once. The virtual environment must be activated again when using a new terminal session, unless the direct `.venv` Python command is used.

## Telegram User Guide

Available commands:

```text
/start - Check that the bot is running
/help  - Show available commands
/reset - Clear the current conversation context
```

Send ordinary text messages to chat with the local model. While Ollama is generating a response, the bot displays `Model is thinking...` and replaces it with the final answer when generation completes.

Example:

```text
User: My name is Alex.
Bot: Nice to meet you, Alex.

User: What is my name?
Bot: Your name is Alex.
```

Use `/reset` to clear the current conversation and begin a fresh context.

## Terminal Client

The project also includes the original interactive terminal client:

```powershell
python .\terminal_client.py
```

It sends messages directly to Ollama without using Telegram. Its conversation history is also stored only in memory for the running process.

## Architecture

The project separates interface, application, and model-server responsibilities.

### `telegram_echo_bot.py`

The Telegram interface and entry point. It:

- Loads the Telegram token from `.env`.
- Polls Telegram for updates.
- Handles `/start`, `/help`, and `/reset`.
- Displays the temporary thinking status.
- Passes text messages to the application layer.
- Sends model responses back to Telegram.
- Reports recoverable model errors to the user.

### `terminal_client.py`

The terminal interface and entry point for direct local testing. It reads terminal input, displays responses, and calls the same application layer used by the Telegram bot.

### `chat_application.py`

The interface-independent conversation layer. Its main function is:

```python
process_user_message(conversation_history, user_message)
```

It prepares the candidate conversation, calls Ollama, and commits the user and assistant messages to history only after a successful response.

### `ollama_client.py`

The Ollama API client. It:

- Stores the Ollama URL, model name, and timeout.
- Builds the chat request payload.
- Sends the HTTP request.
- Parses the JSON response.
- Extracts the assistant message.
- Reports connection, timeout, malformed-response, and empty-response errors.

### Request flow

```text
Telegram message
    -> telegram_echo_bot.py
    -> chat_application.process_user_message()
    -> ollama_client.ask_ollama()
    -> Ollama HTTP API
    -> local model
    -> Telegram reply
```

The Telegram script does not contain duplicate HTTP or Ollama response logic.

## Conversation History

Phase 1 stores one conversation as a Python list in memory:

```python
conversation_history = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hello! How can I help?"},
]
```

The full list is sent to Ollama with each request, so it functions as the model's conversation context. The list is cleared by `/reset` and is automatically lost when the Python process stops or restarts.

There is currently no database, file-based history, multi-user history, or long-term memory.

## Current Progress

### Phase 1: One Chat

Completed:

- Step 1A: Minimal one-prompt terminal client.
- Step 1B: Interactive terminal chat with in-memory context.
- Step 1C: Reusable separation between interface, application logic, and Ollama client.
- Step 2A: Telegram echo bot.
- Step 2B: Telegram connected to the existing Ollama client.
- Step 3: `/reset`, `/help`, thinking status, and basic operational reliability improvements.

The current system supports one Telegram conversation while the bot process is running.

### Deferred Work

The following items are intentionally outside the current prototype:

- Multiple independent Telegram chat histories.
- Persistent conversation storage.
- Automatic context trimming or summarization.
- Telegram user allowlists and access control.
- Splitting responses that exceed Telegram's message limit.
- Streaming model output.
- Automatic startup or hosting as a background service.

See `PLAN.md` and `PLAN_PHASE1.md` for the broader roadmap and detailed architecture decisions.

## Troubleshooting

### The bot does not start

Check that:

- The virtual environment is available.
- Dependencies are installed.
- `.env` exists in the project root.
- `.env` contains `TELEGRAM_BOT_TOKEN`.
- The Telegram token is valid.

### Telegram responds with a model error

Check that Ollama is running and the configured model exists:

```powershell
ollama list
```

Confirm that `MODEL_NAME` in `ollama_client.py` exactly matches an installed model.

### The bot is not responding

Confirm that the VS Code terminal containing `telegram_echo_bot.py` is still running. The bot is active only while that Python process is running.
