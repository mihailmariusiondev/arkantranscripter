from telegram import Update
from telegram.ext import CallbackContext
from config.bot_config import bot_config
from bot.utils.config_utils import get_current_config_status


async def toggle_output_text_file_handler(
    update: Update, context: CallbackContext
) -> None:
    # Alternar la funcionalidad de salida en archivo de texto
    bot_config.toggle_output_text_file()
    # Enviar mensaje de estado al usuario
    await update.message.reply_text(get_current_config_status())
