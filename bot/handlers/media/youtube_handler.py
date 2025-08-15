from typing import Optional
from telegram import Update
from telegram.ext import CallbackContext
from bot.services.youtube_transcript_service import YouTubeTranscriptExtractor
from bot.utils.transcription_utils import extract_video_id, process_media
import logging


async def youtube_handler(
    update: Update, context: CallbackContext, youtube_url: str, original_message
) -> None:
    """
    Enhanced YouTube video transcription handler with multiple service fallback.

    Args:
        update: Telegram update object
        context: Callback context
        youtube_url: URL of the YouTube video
        original_message: Original message containing the URL
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Extract video ID
    video_id = extract_video_id(youtube_url)
    if not video_id:
        logging.warning(f"Invalid YouTube URL from user {user_id}: {youtube_url}")
        await update.message.chat.send_message(
            "No se pudo procesar debido a problemas con el enlace proporcionado."
        )
        return

    logging.info(f"Processing YouTube video {video_id} for user {user_id}")
    await update.message.chat.send_message(
        "Procesando la transcripción del video de YouTube con múltiples servicios, por favor espera..."
    )

    try:
        # Initialize enhanced extractor
        extractor = YouTubeTranscriptExtractor()

        # Extract transcript with fallback
        transcription = await extractor.extract_transcript(video_id)

        if not transcription:
            logging.error(f"All transcript extraction methods failed for video {video_id}")
            await update.message.chat.send_message(
                "No se pudo extraer la transcripción del video. Es posible que no tenga subtítulos disponibles o esté restringido geográficamente."
            )
            return

        logging.info(f"Transcription extracted successfully, length: {len(transcription)} chars")

        # Process the transcription
        await process_media(
            update.message, transcription, original_message, content_type="youtube"
        )
        logging.info(f"Enhanced YouTube transcription completed for video {video_id}")

    except Exception as e:
        logging.error(f"Unexpected error processing YouTube video {video_id}: {str(e)}")
        await update.message.chat.send_message(
            "Ocurrió un error inesperado al procesar la transcripción."
        )
