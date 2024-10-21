import re
import logging
from telegram import Message
import asyncio
import tempfile
from config.constants import CHUNK_SIZE, YOUTUBE_REGEX, PAUSE_BETWEEN_CHUNKS
from openai import OpenAI
from config.bot_config import bot_config
import os

# Initialize OpenAI client with the API key from bot_config
OPENAI_CLIENT = OpenAI(api_key=bot_config.openai_api_key)


def extract_video_id(youtube_url):
    # Extract the video ID from a YouTube URL using regex.
    video_id_match = YOUTUBE_REGEX.search(youtube_url)
    if video_id_match:
        return re.search(r"([\w\-]{11})", youtube_url).group(1)
    return None


async def transcribe_audio(file_path):
    # Transcribe an audio file using OpenAI's Whisper model.
    with open(file_path, "rb") as audio_file:
        transcription = OPENAI_CLIENT.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
    logging.info(f"Transcripción inicial completa:\n{transcription.text}")
    return transcription.text


async def post_process_transcription(transcription):
    # Post-process the transcription using OpenAI's GPT model for minimal corrections.
    logging.info(f"Transcripción original completa:\n{transcription[:50]}...")
    system_prompt = """You are a transcription improvement assistant. Your ONLY task is to make MINIMAL corrections to spelling, punctuation, and sentence structure WITHOUT changing ANY words or their order. Do NOT paraphrase, summarize, or alter the content in any way.

    Rules:
    1. Correct obvious spelling errors ONLY if you are 100% certain.
    2. Add or adjust punctuation ONLY where absolutely necessary for clarity.
    3. DO NOT change any words, even if they seem incorrect or informal.
    4. DO NOT add or remove any content.
    5. Maintain ALL original phrasing, slang, and informal language.
    6. If unsure about a correction, leave the original text as is.
    7. Preserve all original sentence breaks and paragraph structure.

    Your output should be nearly identical to the input, with only the most necessary and minimal changes for spelling and punctuation."""

    response = OPENAI_CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcription},
        ],
        temperature=0.0,
    )

    improved_transcription = response.choices[0].message.content
    logging.info(f"Transcripción mejorada completa:\n{improved_transcription[:50]}...")

    return improved_transcription


async def send_transcription_chunks(
    message: Message, chunks: list[str], original_message: Message
):
    # Send transcription chunks as separate messages.
    await message.chat.send_message(f"Se enviarán {len(chunks)} mensajes.")

    for i, chunk in enumerate(chunks, 1):
        await message.chat.send_message(chunk)

        if i < len(chunks):
            await asyncio.sleep(PAUSE_BETWEEN_CHUNKS)

    # Quote the original message only at the end
    await original_message.reply_text("Transcripción completada.", quote=True)


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


async def process_media(
    message, transcription, original_message, force_transcription=False
):
    # Process the transcription: enhance if enabled, chunk and send, summarize if enabled.
    if bot_config.enhanced_transcription_enabled:
        transcription = await post_process_transcription(transcription)

    if bot_config.output_text_file_enabled:
        # Enviar transcripción como archivo de texto
        await send_transcription_file(message, transcription, original_message)
    else:
        # Enviar transcripción dividida en mensajes
        await message.chat.send_message(
            "Transcripción completada. Enviando resultados..."
        )
        chunks = [
            transcription[i : i + CHUNK_SIZE]
            for i in range(0, len(transcription), CHUNK_SIZE)
        ]
        await send_transcription_chunks(message, chunks, original_message)


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
