from telegram import Update
from telegram.ext import CallbackContext
import logging
from bot.utils.auth_utils import check_auth
from config.bot_config import bot_config
from bot.utils.logging_utils import log_command
from bot.utils.config_utils import get_current_config_status


@check_auth()
async def start_handler(update: Update, context: CallbackContext) -> None:
    """
    Handle the /start command by sending welcome message and current bot status.
    Requires user authentication.
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    logging.info(f"Start command received from user {user_id} in chat {chat_id}")

    # Log current feature configuration
    logging.info(
        "Current bot configuration: "
        + f"auto_transcription={bot_config.auto_transcription_enabled}, "
        + f"enhanced_transcription={bot_config.enhanced_transcription_enabled}, "
        + f"auto_summarize={bot_config.auto_summarize_enabled}"
    )

    # Get current status and send welcome message
    status_message = get_current_config_status()
    welcome_message = (
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

    try:
        await update.message.chat.send_message(f"{welcome_message}\n{status_message}")
        logging.info(f"Welcome message sent successfully to user {user_id}")
    except Exception as e:
        logging.error(
            f"Error sending welcome message to user {user_id}: {str(e)}", exc_info=True
        )
        raise
