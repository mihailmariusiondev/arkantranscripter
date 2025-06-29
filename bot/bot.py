from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, CallbackQueryHandler
from .handlers import (
    start_handler,
    transcribe_handler,
    configure_handler,
    config_callback_handler,
    message_handler,
    error_handler,
    process_queue,
)
import asyncio
from config.bot_config import bot_config


async def setup_bot():

    # Initialize the Telegram bot application
    application = (
        ApplicationBuilder()
        .token(bot_config.bot_token)
        .read_timeout(30)  # Increase timeout to 30 seconds
        .write_timeout(30)  # Increase timeout to 30 seconds
        .connect_timeout(30)  # Increase timeout to 30 seconds
        .build()
    )

    # Add command handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("transcribe", transcribe_handler))
    application.add_handler(CommandHandler("configure", configure_handler))

    # Add callback query handler for configuration buttons
    application.add_handler(CallbackQueryHandler(config_callback_handler))

    # Add message handler for text, video, audio, and voice messages
    application.add_handler(
        MessageHandler(
            filters.TEXT | filters.VIDEO | filters.AUDIO | filters.VOICE,
            message_handler,
        )
    )

    # Add error handler
    application.add_error_handler(error_handler)

    return application


def run_bot():
    # Create and run the event loop
    loop = asyncio.get_event_loop()
    application = loop.run_until_complete(setup_bot())

    # Start the queue processor
    loop.create_task(process_queue())

    # Start the bot
    loop.run_until_complete(application.run_polling())
