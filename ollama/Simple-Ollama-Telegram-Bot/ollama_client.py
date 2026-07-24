import json
import urllib.error
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3.5:2b"
REQUEST_TIMEOUT_SECONDS = 300


def build_request_payload(messages: list[dict]) -> dict:
    return {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
    }


def send_ollama_request(payload: dict) -> dict:
    request_body = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama returned HTTP {error.code}: {error_body}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(
            "Could not connect to Ollama. Make sure Ollama is running at "
            f"{OLLAMA_URL}."
        ) from error
    except TimeoutError as error:
        raise RuntimeError("The request to Ollama timed out.") from error

    try:
        return json.loads(response_body)
    except json.JSONDecodeError as error:
        raise RuntimeError("Ollama returned a response that was not valid JSON.") from error


def extract_model_message(response_data: dict) -> str:
    try:
        message = response_data["message"]
        content = message["content"]
    except KeyError as error:
        raise RuntimeError(
            "Ollama response did not contain the expected message content."
        ) from error

    if not isinstance(content, str):
        raise RuntimeError("Ollama message content was not text.")

    if not content.strip():
        raise RuntimeError("Ollama returned an empty assistant message.")

    return content


def ask_ollama(messages: list[dict]) -> str:
    payload = build_request_payload(messages)
    response_data = send_ollama_request(payload)
    return extract_model_message(response_data)
