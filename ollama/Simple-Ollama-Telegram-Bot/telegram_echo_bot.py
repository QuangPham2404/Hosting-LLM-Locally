import asyncio
import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from chat_application import process_user_message


# Load configuration from the local .env file without putting the token in source code.
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN is missing. Add it to the .env file before starting the bot."
    )


# Handle the /start command and confirm that the bot is running.
async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None:
        return

    await update.message.reply_text("Ollama chat bot is running.")


# Show the commands available to the user.
async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None:
        return

    await update.message.reply_text(
        "/start - Check that the bot is running\n"
        "/reset - Clear the current conversation context\n"
        "/help - Show available commands"
    )


# Clear the current in-memory conversation so the next message starts fresh.
async def reset_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None:
        return

    conversation_history = context.application.bot_data["conversation_history"]
    conversation_history.clear()
    await update.message.reply_text("Conversation history cleared.")


# Send ordinary text messages through the application and Ollama layers.
async def chat_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None or update.message.text is None:
        return

    # Phase 1 uses one in-memory conversation history for the running bot process.
    conversation_history = context.application.bot_data["conversation_history"]
    status_message = await update.message.reply_text("Model is thinking...")

    try:
        # Run the blocking Ollama HTTP call outside Telegram's async event loop.
        answer = await asyncio.to_thread(
            process_user_message,
            conversation_history,
            update.message.text,
        )
    except RuntimeError as error:
        # Keep technical details in the terminal while giving Telegram a safe reply.
        logging.getLogger(__name__).error("Ollama request failed: %s", error)
        await status_message.edit_text(
            "Sorry, I could not get a response from the local model."
        )
        return

    # Replace the temporary status message with the extracted assistant message.
    await status_message.edit_text(answer)


# Log unexpected handler errors without exposing the bot token.
async def handle_error(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logger = logging.getLogger(__name__)
    logger.error("Telegram update failed: %s", context.error)


def main() -> None:
    # Configure basic terminal logging for startup and runtime errors.
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    # Build the Telegram application using the token loaded from .env.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Store the single Phase 1 conversation history in application memory.
    application.bot_data["conversation_history"] = []

    # Register command handling for /start.
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))

    # Register chat handling while excluding commands such as /start.
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message)
    )

    # Register a common error handler for unexpected Telegram/API errors.
    application.add_error_handler(handle_error)

    print("Telegram Ollama chat bot is running. Press Ctrl+C to stop.")

    # Poll Telegram for incoming updates until the process is stopped.
    application.run_polling()


if __name__ == "__main__":
    main()
