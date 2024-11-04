from telegram import Update
from telegram.ext import CallbackContext
from config.bot_config import bot_config
from bot.utils.config_utils import get_current_config_status
import logging


async def toggle_autotranscription_handler(
    update: Update, context: CallbackContext
) -> None:
    """
    Toggle the auto-transcription feature and notify the user of the new state.
    Requires user authentication.
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    logging.info(
        f"Toggle auto-transcription command from user {user_id} in chat {chat_id}"
    )

    try:
        # Toggle the feature and get new state
        new_state = bot_config.toggle_auto_transcription()
        logging.info(f"Auto-transcription toggled to: {new_state}")

        # Get and send updated status
        status_message = get_current_config_status()
        await update.message.reply_text(status_message)
        logging.info(f"Status message sent to user {user_id}")

    except Exception as e:
        logging.error(
            f"Error toggling auto-transcription for user {user_id}: {str(e)}",
            exc_info=True,
        )
        raise
