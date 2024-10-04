import logging
from telegram import Update
from telegram.ext import CallbackContext


async def error_handler(update: object, context: CallbackContext) -> None:
    # Log the error with full traceback
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

    # If the update is available and has an effective message, send an error message to the user
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Ocurrió un error al procesar tu solicitud. Por favor, intenta nuevamente más tarde."
        )
