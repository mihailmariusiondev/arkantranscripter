import logging
from telegram import Update
from telegram.ext import CallbackContext
from bot.handlers.media import (
    youtube_handler,
    video_handler,
    audio_handler,
)
from config.constants import YOUTUBE_REGEX
from bot.utils.auth_utils import check_auth
from bot.utils.logging_utils import log_command


@check_auth()
async def transcribe_handler(update: Update, context: CallbackContext) -> None:
    """
    Main handler for transcription requests. Supports YouTube URLs, videos, and audio messages.
    Requires user authentication.
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    logging.info(f"Transcribe command received from user {user_id} in chat {chat_id}")

    youtube_url = None
    original_message = update.message.reply_to_message or update.message

    try:
        # Check for YouTube URL in different message components
        if original_message.text:
            logging.info(f"Checking text content: {original_message.text[:100]}...")
            video_id_match = YOUTUBE_REGEX.search(original_message.text)
            if video_id_match:
                youtube_url = video_id_match.group()
                logging.info(f"Found YouTube URL in text: {youtube_url}")

        elif original_message.caption:
            logging.info(
                f"Checking caption content: {original_message.caption[:100]}..."
            )
            video_id_match = YOUTUBE_REGEX.search(original_message.caption)
            if video_id_match:
                youtube_url = video_id_match.group()
                logging.info(f"Found YouTube URL in caption: {youtube_url}")

        elif context.args:
            youtube_url = context.args[0]
            logging.info(f"Using URL from command arguments: {youtube_url}")

        # Process media based on type
        if youtube_url:
            logging.info("Processing YouTube URL")
            await youtube_handler(update, context, youtube_url, original_message)

        elif original_message.video:
            logging.info(
                f"Processing video message, file_id: {original_message.video.file_id}"
            )
            await video_handler(original_message, context)

        elif original_message.audio or original_message.voice:
            file_id = (
                original_message.audio.file_id
                if original_message.audio
                else original_message.voice.file_id
            )
            logging.info(f"Processing audio/voice message, file_id: {file_id}")
            await audio_handler(original_message, context)

        else:
            logging.warning(f"No valid media found in message from user {user_id}")
            await update.message.chat.send_message(
                "Por favor, proporciona un enlace de YouTube válido, envía un video o un audio, o cita un mensaje con contenido multimedia."
            )

    except Exception as e:
        logging.error(
            f"Error in transcribe handler for user {user_id}: {str(e)}", exc_info=True
        )
        raise
