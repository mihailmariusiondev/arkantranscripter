import logging
from telegram import Update
from telegram.ext import CallbackContext
from config.constants import YOUTUBE_REGEX
from .transcribe_handler import transcribe_handler, video_handler, audio_handler
import asyncio
from bot.utils.auth_utils import check_auth
from config.bot_config import bot_config

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

@check_auth()
async def message_handler(update: Update, context: CallbackContext) -> None:
    # Añadir el mensaje a la cola
    await message_queue.put((update, context))

async def process_message(update: Update, context: CallbackContext) -> None:
    # Check if auto-transcription is enabled
    if bot_config.auto_transcription_enabled:
        logging.info("Transcripción automática activada")
        # Check if the message contains text or caption
        if update.message.text or update.message.caption:
            text_to_check = update.message.text or update.message.caption
            logging.info(f"Mensaje recibido: {text_to_check}")

            # Check if the message contains a YouTube link
            video_id_match = YOUTUBE_REGEX.search(text_to_check)
            if video_id_match:
                logging.info(f"Enlace de YouTube detectado: {video_id_match.group()}")
                context.args = [video_id_match.group()]
                await transcribe_handler(update, context)
            else:
                logging.info("No se detectó enlace de YouTube")

        # Handle video messages
        elif update.message.video:
            logging.info("Video recibido")
            await video_handler(update.message, context)

        # Handle audio messages
        elif update.message.audio:
            logging.info("Audio recibido")
            await audio_handler(update.message, context)

        # Handle voice messages
        elif update.message.voice:
            logging.info("Mensaje de voz recibido")
            await audio_handler(update.message, context)

        # Log unrecognized message types
        else:
            logging.info("Mensaje no reconocido")
    else:
        logging.info("Transcripción automática desactivada")
