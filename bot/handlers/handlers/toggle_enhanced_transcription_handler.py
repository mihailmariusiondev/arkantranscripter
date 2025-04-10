from telegram import Update
from telegram.ext import CallbackContext
from config.bot_config import bot_config
from bot.utils.config_utils import get_current_config_status


async def toggle_enhanced_transcription_handler(
    update: Update, context: CallbackContext
) -> None:
    # Toggle the enhanced transcription feature
    bot_config.toggle_enhanced_transcription()

    # Send status message to the user
    await update.message.reply_text(get_current_config_status())
