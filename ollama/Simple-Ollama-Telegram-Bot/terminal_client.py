from chat_application import process_user_message


def main() -> None:
    conversation_history = []
    exit_commands = {"/exit", "/quit"}

    print("Interactive chat started. Type /exit or /quit to stop.")

    while True:
        try:
            prompt = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nChat ended.")
            return

        if not prompt:
            continue

        if prompt.lower() in exit_commands:
            print("Chat ended.")
            # Debugging: print the conversation history before exiting
            print("Conversation history:")
            for message in conversation_history:
                role = message["role"]
                content = message["content"]
                print(f"{role.capitalize()}: {content}")
            return

        try:
            answer = process_user_message(conversation_history, prompt)
        except RuntimeError as error:
            print(f"Error: {error}")
            continue
        print(f"\nModel: {answer}")


if __name__ == "__main__":
    main()
