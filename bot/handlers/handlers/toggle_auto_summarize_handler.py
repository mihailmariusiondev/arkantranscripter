from telegram import Update
from telegram.ext import CallbackContext
from config.bot_config import bot_config
from bot.utils.config_utils import get_current_config_status


async def toggle_auto_summarize_handler(
    update: Update, context: CallbackContext
) -> None:
    bot_config.toggle_auto_summarize()
    await update.message.reply_text(get_current_config_status())
