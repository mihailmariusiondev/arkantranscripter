import os
from telegram import Update
from telegram.ext import CallbackContext
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    VideoUnavailable,
)
from bot.utils.transcription_utils import (
    extract_video_id,
    process_media
)
import logging


async def youtube_handler(
    update: Update, context: CallbackContext, youtube_url: str, original_message
) -> None:
    # Extract the video ID from the YouTube URL
    video_id = extract_video_id(youtube_url)
    if not video_id:
        await update.message.chat.send_message(
            "No se pudo procesar debido a problemas con el enlace proporcionado."
        )
        return

    logging.info(f"ID del video a transcribir: {video_id}")
    await update.message.chat.send_message(
        "Procesando la transcripción del video de YouTube, por favor espera..."
    )

    try:
        # Get the list of available transcripts for the video
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Prefer English transcript, fallback to the first available language
        transcript = next(
            (t for t in transcript_list if t.language_code == "en"),
            next(iter(transcript_list)),
        )

        # Fetch the transcript data
        transcript_data = transcript.fetch()

        # Process the transcript into a single string
        transcription = " ".join([entry["text"] for entry in transcript_data])

        # Process the transcription (e.g., enhance, summarize, send chunks)
        await process_media(update.message, transcription, original_message)

    except NoTranscriptFound:
        # Handle case where no transcript is available
        await update.message.chat.send_message(
            "El video no tiene subtítulos disponibles."
        )
    except VideoUnavailable:
        # Handle case where the video is unavailable
        await update.message.chat.send_message(
            "No se pudo procesar debido a problemas con el enlace proporcionado."
        )
    except Exception as e:
        # Log and handle any unexpected errors
        logging.error(f"Error inesperado: {e}")
        await update.message.chat.send_message(
            "Ocurrió un error inesperado al procesar la transcripción."
        )
