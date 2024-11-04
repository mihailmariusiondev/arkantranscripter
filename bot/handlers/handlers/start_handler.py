from telegram import Update
from telegram.ext import CallbackContext
import logging
from bot.utils.auth_utils import check_auth
from config.bot_config import bot_config
from bot.utils.logging_utils import log_command
from bot.utils.config_utils import get_current_config_status


@check_auth()
async def start_handler(update: Update, context: CallbackContext) -> None:
    log_command(update, "start")

    # Handle the /start command.
    # This function sends a welcome message, instructions, and the current status of bot features.
    # It also logs user information and feature status for debugging purposes.

    # Log the current status of various features
    logging.info(f"AUTO_TRANSCRIPTION_ENABLED: {bot_config.auto_transcription_enabled}")
    logging.info(
        f"ENHANCED_TRANSCRIPTION_ENABLED: {bot_config.enhanced_transcription_enabled}"
    )

    # Send welcome message with bot instructions and current feature status
    await update.message.chat.send_message(
        "¡Hola! Soy un bot de transcripción. Puedo transcribir:\n"
        "- Videos de YouTube (usa /transcribe [YouTube URL])\n"
        "- Videos enviados directamente\n"
        "- Archivos de audio\n"
        "- Mensajes de voz\n"
        "También puedes citar cualquier mensaje con contenido multimedia y usar /transcribe para transcribirlo.\n\n"
        "Puedes usar los siguientes comandos para controlar las funciones:\n"
        "/toggle_autotranscription - Activar/desactivar la transcripción automática\n"
        "/toggle_enhanced_transcription - Activar/desactivar la transcripción mejorada\n"
        "/toggle_output_text_file - Activar/desactivar salida en archivo de texto\n"
        "/toggle_auto_summarize - Activar/desactivar resumen automático\n\n"
        f"{get_current_config_status()}\n"
    )
