import logging
from telegram import Update
from telegram.ext import CallbackContext
from config.constants import YOUTUBE_REGEX
from .transcribe_handler import transcribe_handler, video_handler, audio_handler
import asyncio
from config.bot_config import bot_config
from bot.utils.database import db

# Crear una cola global para los mensajes
message_queue = asyncio.Queue()


# Función para procesar los mensajes en la cola
async def process_queue():
    while True:
        update, context = await message_queue.get()
        try:
            await process_message(update, context)
        except Exception as e:
            logging.error(f"Error processing message: {e}")
        finally:
            message_queue.task_done()


async def message_handler(update: Update, context: CallbackContext) -> None:
    # Añadir el mensaje a la cola
    await message_queue.put((update, context))


async def process_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    logging.info(f"Processing message from user {user_id} in chat {chat_id}")

    # Check if auto-transcription is enabled
    if bot_config.auto_transcription_enabled:
        logging.info("Auto-transcription is enabled")
        # Auth check for bot features
        if not str(user_id) in db.get_authorized_users():
            logging.warning(f"Unauthorized access attempt from user {user_id}")
            return

        # Modificar el orden de verificación para priorizar contenido multimedia
        if update.message.video:
            logging.info(
                f"Processing video message, file_id: {update.message.video.file_id}"
            )
            await video_handler(update.message, context)
        elif update.message.audio:
            logging.info(
                f"Processing audio message, file_id: {update.message.audio.file_id}"
            )
            await audio_handler(update.message, context)
        elif update.message.voice:
            logging.info(
                f"Processing voice message, file_id: {update.message.voice.file_id}"
            )
            await audio_handler(update.message, context)
        # Solo procesar texto si no hay contenido multimedia
        elif update.message.text or update.message.caption:
            text_to_check = update.message.text or update.message.caption
            logging.info(
                f"Processing text/caption message: {text_to_check[:100]}..."
            )
            # YouTube link detection
            video_id_match = YOUTUBE_REGEX.search(text_to_check)
            if video_id_match:
                video_url = video_id_match.group()
                logging.info(f"YouTube URL detected: {video_url}")
                context.args = [video_url]
                await transcribe_handler(update, context)
            else:
                logging.info("No YouTube URL found in message")
        else:
            logging.info(f"Unrecognized message type from user {user_id}")
    else:
        logging.info("Auto-transcription is disabled, skipping message processing")
