import logging
import asyncio
from telegram import Update
from telegram.ext import CallbackContext
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    VideoUnavailable,
)
from utils import YOUTUBE_REGEX, CHUNK_SIZE, PAUSE_BETWEEN_CHUNKS, extract_video_id
from config import CACHE, auto_transcription_enabled


async def start(update: Update, context: CallbackContext) -> None:
    logging.info("Comando /start recibido")
    await update.message.reply_text(
        "¡Hola! Soy un bot de transcripción de videos de YouTube. Usa /transcribe [YouTube URL] para obtener la transcripción de un video."
    )


async def transcribe(update: Update, context: CallbackContext) -> None:
    logging.info("Comando /transcribe recibido")
    youtube_url = None
    original_message = update.message

    if update.message.reply_to_message:
        original_text = update.message.reply_to_message.text
        video_id_match = YOUTUBE_REGEX.search(original_text)
        if video_id_match:
            youtube_url = video_id_match.group()
            original_message = update.message.reply_to_message
    elif context.args:
        youtube_url = context.args[0]

    if not youtube_url:
        await update.message.reply_text(
            "Por favor, proporciona un enlace de YouTube válido."
        )
        return

    video_id = extract_video_id(youtube_url)
    if not video_id:
        await update.message.reply_text(
            "No se pudo procesar debido a problemas con el enlace proporcionado."
        )
        return

    logging.info(f"ID del video a transcribir: {video_id}")
    await update.message.reply_text(
        "Procesando la transcripción del video de YouTube, por favor espera..."
    )

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = next(
            (t for t in transcript_list if t.language_code == "en"),
            next(iter(transcript_list)),
        )
        transcript_data = transcript.fetch()

        chunks = []
        current_chunk = ""
        for entry in transcript_data:
            if len(current_chunk) + len(entry["text"]) > CHUNK_SIZE:
                chunks.append(current_chunk)
                current_chunk = entry["text"] + " "
            else:
                current_chunk += entry["text"] + " "
        if current_chunk:
            chunks.append(current_chunk)

        CACHE[video_id] = chunks

        await update.message.reply_text(
            f"Transcripción completa en {transcript.language}. Se enviarán {len(chunks)} mensajes."
        )

        for i, chunk in enumerate(chunks, 1):
            await update.message.reply_text(chunk)
            if i < len(chunks):
                await asyncio.sleep(PAUSE_BETWEEN_CHUNKS)

        await original_message.reply_text(
            "Transcripción completada para este video.", quote=True
        )

    except NoTranscriptFound:
        await update.message.reply_text("El video no tiene subtítulos disponibles.")
    except VideoUnavailable:
        await update.message.reply_text(
            "No se pudo procesar debido a problemas con el enlace proporcionado."
        )
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        await update.message.reply_text(
            "Ocurrió un error inesperado al procesar la transcripción."
        )


async def toggle_autotranscription(update: Update, context: CallbackContext) -> None:
    global auto_transcription_enabled
    auto_transcription_enabled = not auto_transcription_enabled
    status = "activada" if auto_transcription_enabled else "desactivada"
    await update.message.reply_text(f"Transcripción automática {status}.")


async def handle_message(update: Update, context: CallbackContext) -> None:
    if auto_transcription_enabled and not update.message.text.startswith("/"):
        video_id_match = YOUTUBE_REGEX.search(update.message.text)
        if video_id_match:
            context.args = [video_id_match.group()]
            await transcribe(update, context)
