import re
import logging
from telegram import Message
import asyncio
import tempfile
from config.constants import CHUNK_SIZE, YOUTUBE_REGEX, PAUSE_BETWEEN_CHUNKS
from bot.services.openai_service import openai_service
import os
from config.bot_config import bot_config


def extract_video_id(youtube_url):
    # Extract the video ID from a YouTube URL using regex.
    video_id_match = YOUTUBE_REGEX.search(youtube_url)
    if video_id_match:
        return re.search(r"([\w\-]{11})", youtube_url).group(1)
    return None


async def transcribe_audio(file_path):
    """Transcribe an audio file using OpenAI's Whisper model."""
    return await openai_service.transcribe_audio(file_path)


async def post_process_transcription(transcription):
    """Post-process the transcription using OpenAI's GPT model."""
    return await openai_service.post_process_transcription(transcription)


async def send_transcription_chunks(
    message: Message, chunks: list[str], original_message: Message
):
    # Send transcription chunks as replies to the original message.
    for chunk in chunks:
        await original_message.reply_text(chunk, quote=True)
        await asyncio.sleep(PAUSE_BETWEEN_CHUNKS)


async def send_transcription_file(
    message: Message, transcription: str, original_message: Message
):
    """
    Envía la transcripción como un archivo de texto plano.
    """
    try:
        # Crear un archivo temporal con la transcripción
        temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".txt").name
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(transcription)
        logging.info(f"Archivo de transcripción creado en: {temp_file_path}")

        # Enviar el archivo al usuario
        with open(temp_file_path, "rb") as file:
            await message.chat.send_document(
                document=file,
                filename="transcripcion.txt",
                caption="Aquí tienes la transcripción en un archivo de texto.",
            )
        logging.info("Archivo de transcripción enviado correctamente.")
    except Exception as e:
        logging.error(f"Error al enviar el archivo de transcripción: {e}")
        await message.reply_text(
            "Ocurrió un error al enviar la transcripción como archivo de texto."
        )
    finally:
        # Eliminar el archivo temporal
        try:
            os.unlink(temp_file_path)
            logging.info(f"Archivo temporal eliminado: {temp_file_path}")
        except Exception as e:
            logging.error(f"Error al eliminar el archivo temporal: {e}")


async def process_media(message, transcription, original_message, content_type="video"):
    """
    Process media content by handling transcription, chunking, and optional summarization.

    Args:
        message: The Telegram message object
        transcription: The raw transcription text
        original_message: The original message being processed
        content_type: Type of media being processed (video/audio/youtube)
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        logging.info(
            f"Processing {content_type} media for user {user_id} in chat {chat_id}"
        )

        # Enhanced transcription processing if enabled
        if bot_config.enhanced_transcription_enabled:
            logging.info("Enhanced transcription enabled, post-processing text")
            transcription = await openai_service.post_process_transcription(
                transcription
            )
            logging.info("Enhanced transcription completed")

        # Handle text file output if enabled
        if bot_config.output_text_file_enabled:
            logging.info("Text file output enabled, preparing file")
            await send_transcription_file(message, transcription, original_message)
        else:
            # Split transcription into chunks
            chunks = [
                transcription[i : i + CHUNK_SIZE]
                for i in range(0, len(transcription), CHUNK_SIZE)
            ]
            logging.info(f"Split transcription into {len(chunks)} chunks")

            await send_transcription_chunks(message, chunks, original_message)

    except Exception as e:
        logging.error(f"Error processing media: {str(e)}", exc_info=True)
        raise


def get_file_size(file_path):
    """Get human-readable file size."""
    size_bytes = os.path.getsize(file_path)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0


async def compress_audio(input_path, output_path):
    """Compress audio using ffmpeg with Opus codec."""
    try:
        input_size = get_file_size(input_path)
        logging.info(f"Compressing audio. Input file size: {input_size}")

        # Construir el comando de ffmpeg
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-acodec",
            "libopus",
            "-ac",
            "1",
            "-b:a",
            "12k",
            "-application",
            "voip",
            output_path,
        ]

        # Ejecutar ffmpeg de manera asíncrona
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Esperar a que el proceso termine
        stdout, stderr = await process.communicate()

        # Verificar si el proceso terminó correctamente
        if process.returncode != 0:
            logging.error(f"Error compressing audio: {stderr.decode()}")
            raise Exception(f"ffmpeg exited with code {process.returncode}")

        output_size = get_file_size(output_path)
        logging.info(f"Audio compression complete. Output file size: {output_size}")
        return output_path

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise


async def extract_audio(input_path, output_path):
    """Extract audio from video using ffmpeg."""
    try:
        input_size = get_file_size(input_path)
        logging.info(f"Extracting audio from video. Input file size: {input_size}")

        # Construir el comando de ffmpeg
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-vn",  # No incluir video en la salida
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            "16000",
            output_path,
        ]

        # Ejecutar ffmpeg de manera asíncrona
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Esperar a que el proceso termine
        stdout, stderr = await process.communicate()

        # Verificar si el proceso terminó correctamente
        if process.returncode != 0:
            logging.error(f"Error extracting audio: {stderr.decode()}")
            raise Exception(f"ffmpeg exited with code {process.returncode}")

        output_size = get_file_size(output_path)
        logging.info(f"Audio extraction complete. Output file size: {output_size}")
        return output_path

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise
