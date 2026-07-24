# Phase 1 Plan

## Step 1A - Minimal One-Prompt Terminal Client

### Objective

Build the smallest working Python client that sends one terminal prompt to the local Ollama API and prints the extracted model response.

This prototype is meant to prove that the Python application can communicate with the Ollama server before Telegram, conversation history, persistence, or multi-user behavior are added.

Initial flow:

```text
Terminal input
    -> Python script
    -> Ollama HTTP API at localhost:11434
    -> Local model response
    -> Python script extracts assistant text
    -> Terminal output
```

### Scope

Included:

- Read one user prompt from the terminal.
- Build a valid Ollama chat API request payload.
- Send the request to the local Ollama server.
- Receive and parse the API response.
- Extract the assistant's generated message.
- Print the assistant's message to the terminal.
- Handle basic connection, timeout, HTTP, JSON, and malformed-response errors.

Excluded:

- Telegram integration.
- Interactive chat loop.
- Conversation history.
- Multiple users or multiple chats.
- Persistent storage.
- Long-term memory.
- Advanced runtime configuration.

### Proposed Script Structure

The first prototype should be a single Python script with clear internal function boundaries.

Core functions:

```python
def build_request_payload(prompt: str) -> dict:
    ...


def send_ollama_request(payload: dict) -> dict:
    ...


def extract_model_message(response_data: dict) -> str:
    ...


def main() -> None:
    ...
```

### Function Responsibilities

#### `build_request_payload(prompt: str) -> dict`

Purpose:

Convert the user's terminal message into the JSON structure expected by Ollama's chat API.

Expected payload shape:

```python
{
    "model": MODEL_NAME,
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "stream": False,
}
```

Notes:

- `stream` should be set to `False` for the first prototype so the response comes back as one complete JSON object.
- The model name should be defined near the top of the script as a simple constant for now.

#### `send_ollama_request(payload: dict) -> dict`

Purpose:

Send the HTTP request to the Ollama server and return the parsed JSON response.

Responsibilities:

- Send a `POST` request to the Ollama chat endpoint.
- Use the local Ollama server URL:

```text
http://localhost:11434/api/chat
```

- Apply a reasonable timeout.
- Detect common request problems:
  - Ollama server is not running.
  - Request times out.
  - Ollama returns an HTTP error.
  - Response body is not valid JSON.

This function owns the server communication boundary.

#### `extract_model_message(response_data: dict) -> str`

Purpose:

Receive Ollama's parsed API response and extract only the assistant's generated text.

Expected response field:

```python
response_data["message"]["content"]
```

Responsibilities:

- Understand the Ollama response structure.
- Return only the assistant message string.
- Raise a clear error if the expected field is missing or malformed.

This function should not print to the terminal. It only extracts the model text so it can be reused later by other interfaces.

#### `main() -> None`

Purpose:

Coordinate the terminal prototype.

Responsibilities:

- Read one prompt from terminal input.
- Reject an empty prompt.
- Call `build_request_payload()`.
- Call `send_ollama_request()`.
- Call `extract_model_message()`.
- Print the final model response to the terminal.
- Show user-friendly error messages.

The terminal input/output behavior belongs here, not inside the Ollama communication functions.

### Execution Flow

```text
main()
    -> input("You: ")
    -> build_request_payload(prompt)
    -> send_ollama_request(payload)
    -> extract_model_message(response_data)
    -> print("Model:", answer)
    -> exit
```

### Design Principle

Keep the script simple, but separate the important boundaries:

```text
Terminal interface
    -> request construction
    -> Ollama HTTP communication
    -> response extraction
```

This keeps the Ollama-facing logic reusable when later milestones add an interactive terminal chat and Telegram integration.

## Step 1B - Interactive Terminal Chat

### Objective

Extend the Step 1A one-prompt client into a multi-turn terminal conversation. The user should be able to send multiple messages during one program run, while Ollama receives enough previous conversation context to generate relevant replies.

### Scope

Included:

- Run an interactive input/output loop until the user exits.
- Maintain conversation history in memory during the current program run.
- Send the complete current conversation history with each Ollama request.
- Add both user messages and assistant responses to the history after successful turns.
- Support `/exit` and `/quit` commands.
- Handle empty input, `Ctrl+C`, and end-of-file gracefully.
- Continue the chat after a recoverable request error.

Excluded:

- Saving history to a file or database.
- Restoring history after the program exits.
- Separate histories for multiple users or chats.
- Telegram integration.
- Streaming responses.
- Automatic history trimming or summarization.

### History Storage Architecture

Conversation history will be stored as a Python list in memory:

```python
conversation_history = []
```

Each entry in the list will be a dictionary containing exactly the message role and text content:

```python
conversation_history = [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language."},
]
```

The supported roles are:

- `user`: a message written by the terminal user.
- `assistant`: a response generated by Ollama.

Before each request, Ollama receives the current list through the payload's `messages` field. The list is process-local and exists only for the lifetime of the Python program. It is discarded when the program exits, so this implementation does not provide persistence or recovery.

This storage method is intentionally simple for the prototype, but it defines an important future upgrade boundary. Later stages can replace or wrap the list with a database-backed conversation store, file storage, or per-user/per-chat histories without changing the Ollama request and response functions. The later design will also need to address history size, trimming, summarization, and privacy.

### Proposed Script Structure

The existing single-file structure from Step 1A should be extended rather than split into multiple modules at this stage.

The request-building function should accept the full message list instead of a single prompt:

```python
def build_request_payload(messages: list[dict]) -> dict:
    ...
```

The other Ollama-facing functions remain separated:

```python
def send_ollama_request(payload: dict) -> dict:
    ...


def extract_model_message(response_data: dict) -> str:
    ...


def main() -> None:
    ...
```

### Function Responsibilities

#### `build_request_payload(messages: list[dict]) -> dict`

Create the Ollama chat payload using the configurable `MODEL_NAME` and the complete conversation history:

```python
{
    "model": MODEL_NAME,
    "messages": messages,
    "stream": False,
}
```

This function should not manage the history itself. The terminal loop owns the conversation state and passes the current messages into this function.

#### `send_ollama_request(payload: dict) -> dict`

Send one non-streaming request to Ollama and return the parsed JSON response. It continues to own the server communication boundary, including the configured request timeout and connection, HTTP, and JSON errors.

#### `extract_model_message(response_data: dict) -> str`

Extract and return the assistant text from Ollama's response. It should not print output or modify conversation history.

#### `main() -> None`

Own the interactive terminal loop and the in-memory history:

1. Create an empty `conversation_history` list.
2. Read a message from the terminal.
3. Exit when the user enters `/exit`, `/quit`, presses `Ctrl+C`, or reaches end-of-file.
4. Ignore empty messages.
5. Create a candidate message list containing the existing history plus the new user message.
6. Build and send the request using that candidate list.
7. Extract and print the assistant response.
8. Commit both the user message and assistant response to `conversation_history` only after a successful response.
9. Repeat until exit.

Only successful user/assistant exchanges should be stored. If a request fails, the failed user message should not remain in the history for the next attempt.

### Execution Flow

```text
main()
    -> conversation_history = []
    -> read user message
    -> create candidate history with the new user message
    -> build_request_payload(candidate history)
    -> send_ollama_request(payload)
    -> extract_model_message(response)
    -> append user message and assistant response to history
    -> print assistant response
    -> repeat
```

### Design Principle

The terminal interface owns the temporary conversation state. The Ollama functions remain stateless: they receive input, perform one operation, and return output. This keeps the prototype easy to understand and preserves a clear boundary for replacing the list with persistent, user-specific storage in later stages.

## Step 1C - Reusable Internal Separation

### Objective

Separate the terminal interface, conversation/application logic, and Ollama API client so the terminal code can later be replaced by Telegram code without duplicating the conversation or model-server logic.

### Design Decision

Split the current single script into three Python files:

```text
terminal_client.py
chat_application.py
ollama_client.py
```

The user will continue to launch only the terminal entry point:

```powershell
python .\terminal_client.py
```

The observable terminal behavior should remain the same. This step changes the internal organization of the code, not the user workflow.

### Module Responsibilities

#### `terminal_client.py` - Terminal Interface

This file will be the executable entry point. It will be responsible for:

- Displaying prompts and model responses.
- Reading messages from terminal input.
- Handling empty input.
- Handling `/exit`, `/quit`, `Ctrl+C`, and end-of-file.
- Maintaining the current terminal session's history list or passing it to the application layer.
- Calling the conversation/application function.

It will not contain HTTP request construction or direct communication with Ollama.

#### `chat_application.py` - Conversation/Application Logic

This file will contain interface-independent chat behavior, including a reusable function such as:

```python
def process_user_message(
    conversation_history: list[dict],
    user_message: str,
) -> str:
    ...
```

It will be responsible for:

- Creating the candidate history containing the new user message.
- Calling the Ollama client.
- Adding the user and assistant messages to history only after a successful response.
- Returning the assistant response to the interface.

It will not read terminal input, print terminal output, or contain Telegram-specific code.

#### `ollama_client.py` - Ollama API Client

This file will contain all model-server communication and configuration:

- `OLLAMA_URL`.
- `MODEL_NAME`.
- `REQUEST_TIMEOUT_SECONDS`.
- `build_request_payload(messages)`.
- `send_ollama_request(payload)`.
- `extract_model_message(response_data)`.
- A reusable `ask_ollama(messages)` function that coordinates the API operations.

It will not manage conversation history or know whether the caller is the terminal or Telegram.

### Dependency Flow

Dependencies should point inward from the interface toward reusable logic:

```text
terminal_client.py
    -> chat_application.py
        -> ollama_client.py
            -> Ollama HTTP API
```

Later, Telegram code can use the same application and API layers:

```text
terminal_client.py  -\
                     -> chat_application.py -> ollama_client.py -> Ollama
Telegram handler   -/
```

The Telegram handler will therefore not reimplement request construction, HTTP communication, response extraction, or single-chat history behavior.

### Scope Boundary

Step 1C is an internal refactoring and reuse milestone. It does not add Telegram integration, persistent storage, multiple-user histories, or a database. The in-memory list from Step 1B remains the temporary history mechanism until later phases require a storage upgrade.

## Step 2A - Telegram Echo Bot

### Objective

Build and verify the Telegram communication layer independently from Ollama. The bot should receive Telegram messages and return either a fixed startup response or the same text that the user sent.

This milestone proves that the Python application can connect to Telegram, receive updates, process messages, and send replies before the Ollama model server is added to the flow.

### Scope

Included:

- Create a Telegram bot through BotFather.
- Install and use the `python-telegram-bot` library.
- Store the Telegram bot token outside the source code.
- Create a separate `telegram_echo_bot.py` entry point.
- Start the bot using Telegram polling.
- Implement a `/start` command with a fixed reply.
- Implement a text-message handler that echoes the received text.
- Handle missing configuration and basic Telegram connection errors.
- Stop the bot cleanly with `Ctrl+C`.

Excluded:

- Ollama API calls.
- Model inference.
- Conversation history.
- Use of `chat_application.py` or `ollama_client.py`.
- Multiple users or per-chat storage.
- Database or persistent storage.
- Access control beyond the basic bot setup.
- Webhook deployment or public hosting.

### Proposed Script Structure

Create a new standalone Telegram entry point:

```text
telegram_echo_bot.py
```

The existing terminal prototype files remain unchanged during this milestone:

```text
terminal_client.py
chat_application.py
ollama_client.py
```

The Step 2A execution flow is:

```text
Telegram user
    -> Telegram servers
    -> telegram_echo_bot.py
    -> command or text handler
    -> fixed reply or echoed text
    -> Telegram user
```

### Configuration and Security

The bot token must be read from an environment variable:

```text
TELEGRAM_BOT_TOKEN
```

The token must not be hard-coded in `telegram_echo_bot.py`, committed to the repository, or printed in logs. The program should stop with a clear configuration error if the variable is missing.

### Python Environment and Token Storage

The project uses a Python virtual environment in the `.venv` directory:

```text
.venv/
```

The virtual environment isolates this project's Python interpreter and installed dependencies from the system-wide Python installation. It is not the token store and should not be treated as a permanent data directory because it can be deleted and recreated.

The Telegram token is stored separately in a project-level `.env` file:

```text
.env
```

Its contents follow this format:

```text
TELEGRAM_BOT_TOKEN=your-token-here
```

`telegram_echo_bot.py` loads this value at startup using `python-dotenv`. This keeps the token out of the Python source code. The `.env` file must not be committed to the repository or exposed in logs. The token is therefore protected by separation of responsibilities:

```text
.venv -> Python environment and dependencies
.env  -> local Telegram token configuration
```

### Running and Restarting the Bot

The bot is an actively running Python process, not a permanently hosted service. Telegram messages can be received only while this process is running and connected to Telegram.

From a new VS Code terminal session, use:

```powershell
cd "D:\Extra storage\Hosting-LLM-Locally\ollama\Simple-Ollama-Telegram-Bot"
.\.venv\Scripts\Activate.ps1
python .\telegram_echo_bot.py
```

The virtual environment must be activated again when a new terminal session is opened. Dependencies do not need to be reinstalled each time, and the token does not need to be re-entered because it remains in `.env`.

The bot can also be started without manually activating the environment:

```powershell
.\.venv\Scripts\python.exe .\telegram_echo_bot.py
```

Keep the VS Code terminal and the running script open while using the bot. Pressing `Ctrl+C`, closing the terminal, or stopping the Python process deactivates the bot until the script is started again.

### Handler Responsibilities

#### `/start` handler

Respond with a fixed message confirming that the echo bot is running. This tests command handling separately from ordinary text handling.

#### Text-message handler

Receive ordinary text and send the exact same text back to the originating Telegram chat. This handler must not call Ollama or modify conversation history.

#### Unsupported-message behavior

Ignore or safely acknowledge unsupported message types such as images, documents, or stickers. These message types are outside the Step 2A objective.

### Milestones

1. Create the bot with BotFather and obtain its token.
2. Install the Telegram bot library.
3. Configure `TELEGRAM_BOT_TOKEN` outside the source code.
4. Start a minimal polling application.
5. Add and test the `/start` handler.
6. Add and test the text echo handler.
7. Add basic configuration, connection, and shutdown handling.

### Manual Completion Criteria

Step 2A is complete when:

- The bot appears online in Telegram while the Python process is running.
- `/start` receives the fixed startup reply.
- Ordinary text messages are echoed exactly.
- Multiple messages can be handled during one run.
- The bot does not call Ollama.
- The token is not stored in source code.
- The process can be stopped cleanly with `Ctrl+C`.

### Design Boundary

Step 2A isolates Telegram communication. Step 2B will replace the echo behavior with a call to the existing reusable application and Ollama client layers:

```text
Telegram message
    -> Telegram handler
    -> chat_application.py
    -> ollama_client.py
    -> Ollama server
```

## Step 2B - Connect Telegram to the Existing Ollama Client

### Objective

Replace the Step 2A echo response with a response generated by the locally hosted Ollama model. Telegram remains the user interface, while the existing application and Ollama client layers handle conversation processing and model-server communication.

### Design Decision

Do not create a second polling script. The existing `telegram_echo_bot.py` already starts the Telegram application and polls Telegram for updates through:

```python
application.run_polling()
```

For Step 2B, this same file becomes the Telegram-to-Ollama entry point. Its text-message handler will change from echoing the received text to calling the existing reusable application function.

The user will continue to start the bot with:

```powershell
python .\telegram_echo_bot.py
```

The filename may be renamed to `telegram_bot.py` in a later cleanup if desired, but renaming is not required for this integration milestone.

### End-to-End Architecture

```text
Telegram user
    -> Telegram servers
    -> telegram_echo_bot.py polling process
    -> Telegram message handler
    -> chat_application.process_user_message()
    -> ollama_client.ask_ollama()
    -> Ollama HTTP API at localhost:11434
    -> local model response
    -> response extraction
    -> Telegram message handler
    -> Telegram user
```

### Reuse of Existing Components

The existing modules are designed for direct composition and should not require duplicated logic or a major rewrite.

#### `ollama_client.py`

Remains responsible for:

- Ollama URL configuration.
- Model name configuration.
- Request timeout configuration.
- Building the API payload.
- Sending the HTTP request.
- Parsing the JSON response.
- Extracting the assistant message.

The Telegram layer does not construct HTTP requests and does not inspect Ollama response fields directly.

#### `chat_application.py`

Remains responsible for:

- Receiving the current conversation history and Telegram message text.
- Creating the candidate history for the request.
- Calling `ask_ollama()`.
- Adding the user and assistant messages after a successful response.
- Returning the assistant text to the caller.

Its existing interface is suitable for Telegram:

```python
answer = process_user_message(
    conversation_history,
    user_message,
)
```

Because failed requests do not commit the user message to history, an Ollama error will not corrupt the conversation state.

#### `telegram_echo_bot.py`

Becomes responsible for:

- Loading the Telegram token from `.env`.
- Starting Telegram polling.
- Receiving Telegram updates.
- Maintaining the single Phase 1 in-memory conversation history.
- Passing message text to `process_user_message()`.
- Sending the returned model response back to the originating Telegram chat.
- Translating recoverable Ollama errors into a user-friendly Telegram message.

The existing `/start` handler remains a Telegram-only startup response. The existing echo handler is replaced by a chatbot message handler.

### Conversation History

Phase 1 continues to support one active conversation. The Telegram entry point will maintain one in-memory list:

```python
conversation_history = []
```

Each successful Telegram exchange adds:

```python
{"role": "user", "content": user_message}
{"role": "assistant", "content": model_response}
```

The history is lost when the bot process stops. Per-chat histories, persistence, and database storage remain deferred to Phase 2.

### Asynchronous Telegram and Synchronous Ollama Boundary

The `python-telegram-bot` handlers are asynchronous, while the current Ollama client uses blocking standard-library HTTP calls. The Telegram handler should call the existing synchronous application function through a worker thread:

```python
answer = await asyncio.to_thread(
    process_user_message,
    conversation_history,
    update.message.text,
)
```

This allows the Telegram event loop to remain responsive while Ollama loads the model or generates a response. The Ollama client itself does not need to be rewritten as asynchronous for this milestone.

### Error Handling

The Telegram handler should catch `RuntimeError` raised by the application or Ollama client and send a concise message such as:

```text
Sorry, I could not get a response from the local model.
```

Detailed technical errors should remain in the terminal logs rather than being exposed unnecessarily to the Telegram user. Unexpected Telegram errors continue to be handled by the bot's registered error handler.

### Scope Boundary

Included:

- Telegram-to-Ollama message flow.
- Reuse of `chat_application.py` and `ollama_client.py`.
- One in-memory conversation history.
- Non-streaming model responses.
- Basic user-facing error handling.

Excluded:

- Multiple independent Telegram chat histories.
- Persistent conversation storage.
- `/reset` history management unless added as a later reliability feature.
- Streaming model output.
- Access control and user allowlists.
- Telegram webhook deployment.

### Step 2B Completion Criteria

Step 2B is complete when:

- A Telegram text message reaches the running Python bot.
- The message is passed through `chat_application.py` and `ollama_client.py`.
- Ollama generates a response using the configured local model.
- The response is sent back to the originating Telegram chat.
- Multiple messages retain context during the running bot session.
- Ollama connection or timeout errors do not crash the bot process.
- No duplicate Ollama request logic exists in the Telegram script.

## Step 3 - Reliability and Single-Chat Improvements

### Objective

Improve the usability and reliability of the working single-chat Telegram-to-Ollama bot without introducing persistence, multi-user storage, streaming, or other production-level complexity.

### Step 3 Scope

This step will add four focused improvements:

1. A `/reset` command for manually clearing the current conversation context.
2. A temporary `Model is thinking...` status message while Ollama generates a response.
3. A `/help` command explaining the available bot commands.
4. More consistent handling of common operational failures.

### `/reset` Command

Add a Telegram command handler that clears the current Phase 1 in-memory history:

```python
context.application.bot_data["conversation_history"].clear()
```

The bot will confirm the action with a message such as:

```text
Conversation history cleared.
```

This gives the user a manual way to start a fresh context without stopping and restarting the Python process.

### Thinking Status Message

When a normal text message arrives, the Telegram handler will:

1. Send a temporary `Model is thinking...` message.
2. Call the existing `process_user_message()` function.
3. Replace the temporary message with the model response.
4. Replace it with a friendly error message if Ollama fails.

This provides feedback during non-streaming generation. Live token or thinking output is explicitly deferred and will require a separate streaming design.

### `/help` Command

Add a fixed help response describing the current commands:

```text
/start - Check that the bot is running
/reset - Clear the current conversation context
/help - Show available commands
```

The help message will describe the actual commands implemented by the bot and will not expose internal implementation details.

### Operational Reliability

The existing error boundaries will be strengthened so that:

- Ollama being offline produces a clear Telegram error message.
- A request timeout produces a clear Telegram error message.
- Failed requests do not enter the conversation history.
- Empty model responses are detected instead of silently sending a blank message.
- Technical error details are logged in the VS Code terminal without unnecessarily exposing them to Telegram users.
- Recoverable Ollama errors do not terminate the Telegram bot process.
- Restarting the Python process continues to produce a new empty in-memory conversation.

The Ollama client remains responsible for HTTP, timeout, JSON, and malformed-response errors. The Telegram handler remains responsible for converting recoverable application errors into user-facing messages.

### Expected File Changes

The primary changes will be made in:

```text
telegram_echo_bot.py
```

This file will receive the `/reset` and `/help` handlers, the temporary thinking-status behavior, and improved Telegram-facing error handling.

The following file may receive a small validation change:

```text
ollama_client.py
```

Its response extraction function may reject empty assistant content with a clear `RuntimeError` so blank responses are handled consistently.

No new script, database, persistent storage, or history-management module is required for this step.

### Deferred Improvements

The following improvements remain outside this Step 3 scope:

- Telegram user allowlists and access control.
- Splitting responses that exceed Telegram's message-length limit.
- Persistent conversation history.
- Multiple independent chat histories.
- Streaming model output.
- Automatic context trimming or summarization.

### Step 3 Completion Criteria

Step 3 is complete when:

- `/reset` clears the active conversation context.
- `/help` displays the available commands.
- Users see `Model is thinking...` during model generation.
- Successful responses replace the status message.
- Ollama failures produce a useful Telegram message and do not stop the bot.
- Empty responses are handled explicitly.
- The existing terminal and Telegram-to-Ollama architecture remains reusable.
