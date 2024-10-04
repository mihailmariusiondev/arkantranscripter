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
    log_command(update, "transcribe")

    youtube_url = None
    # Get the original message (either the replied-to message or the current message)
    original_message = update.message.reply_to_message or update.message

    # Check for YouTube URL in text or caption
    if original_message.text:
        video_id_match = YOUTUBE_REGEX.search(original_message.text)
        if video_id_match:
            youtube_url = video_id_match.group()
    elif original_message.caption:
        video_id_match = YOUTUBE_REGEX.search(original_message.caption)
        if video_id_match:
            youtube_url = video_id_match.group()
    elif context.args:
        youtube_url = context.args[0]

    # Handle different types of media
    if youtube_url:
        # Process YouTube URL
        await youtube_handler(update, context, youtube_url, original_message)
    elif original_message.video:
        # Process video file
        await video_handler(original_message, context)
    elif original_message.audio or original_message.voice:
        # Process audio or voice message
        await audio_handler(original_message, context)
    else:
        # Send error message if no valid media is found
        await update.message.chat.send_message(
            "Por favor, proporciona un enlace de YouTube válido, envía un video o un audio, o cita un mensaje con contenido multimedia."
        )
