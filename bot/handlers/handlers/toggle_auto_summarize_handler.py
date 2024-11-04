from telegram import Update
from telegram.ext import CallbackContext
from bot.utils.auth_utils import check_auth
from config.bot_config import bot_config
from bot.utils.logging_utils import log_command
from bot.utils.config_utils import get_current_config_status

@check_auth()
async def toggle_auto_summarize_handler(
    update: Update, context: CallbackContext
) -> None:
    log_command(update, "toggle_auto_summarize")
    bot_config.toggle_auto_summarize()
    await update.message.reply_text(get_current_config_status()) 