from ollama_client import ask_ollama


def process_user_message(
    conversation_history: list[dict],
    user_message: str,
) -> str:
    user_message_entry = {"role": "user", "content": user_message}
    request_history = conversation_history + [user_message_entry]
    answer = ask_ollama(request_history)

    conversation_history.extend(
        [
            user_message_entry,
            {"role": "assistant", "content": answer},
        ]
    )

    return answer
