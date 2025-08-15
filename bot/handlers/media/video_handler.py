import tempfile
import os
import logging
from telegram import Message
from telegram.ext import CallbackContext
from bot.utils.transcription_utils import (
    transcribe_audio,
    process_media,
    compress_audio,
    extract_audio,
    get_file_size,
)
from config.constants import MAX_FILE_SIZE


async def video_handler(message: Message, context: CallbackContext) -> None:
    """
    Handle video message transcription requests.

    Args:
        message: Telegram message containing video
        context: Callback context
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    file_id = message.video.file_id
    file_size = message.video.file_size

    logging.info(f"Processing video from user {user_id}, file_id: {file_id}")
    logging.info(f"Video file size: {file_size} bytes")

    # Check file size limit
    if file_size > MAX_FILE_SIZE:
        logging.warning(
            f"Video size {file_size} exceeds limit of {MAX_FILE_SIZE} bytes"
        )
        await message.chat.send_message(
            f"📹 **Video demasiado grande**\n"
            f"📊 Tamaño: {file_size/1024/1024:.1f} MB\n"
            f"⚠️ Límite máximo: {MAX_FILE_SIZE/1024/1024:.0f} MB\n"
            f"💡 Por favor, envía un archivo más pequeño."
        )
        return

    # Send initial status message
    status_message = await message.chat.send_message(
        f"🎬 **Procesando video**\n"
        f"📊 Tamaño: {file_size/1024/1024:.1f} MB\n"
        f"🔄 Descargando archivo..."
    )

    # Create temporary files
    temp_file_path = None
    audio_file_path = None
    compressed_file_path = None

    try:
        # Get video file from Telegram
        file = await context.bot.get_file(file_id)
        logging.info(f"Retrieved file info: {file.file_path}")

        # Create temporary files
        temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        audio_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        compressed_file_path = tempfile.NamedTemporaryFile(
            delete=False, suffix=".ogg"
        ).name

        # Download video
        await status_message.edit_text(
            f"🎬 **Procesando video**\n"
            f"📊 Tamaño: {file_size/1024/1024:.1f} MB\n"
            f"⬇️ Descargando archivo de Telegram..."
        )

        await file.download_to_drive(custom_path=temp_file_path)
        logging.info(
            f"Video downloaded successfully, size: {get_file_size(temp_file_path)}"
        )

        # Extract audio from video
        await status_message.edit_text(
            f"🎬 **Procesando video**\n"
            f"📊 Tamaño: {file_size/1024/1024:.1f} MB\n"
            f"🎵 Extrayendo audio del video..."
        )

        await extract_audio(temp_file_path, audio_file_path)
        logging.info(f"Audio extracted, size: {get_file_size(audio_file_path)}")

        # Compress extracted audio
        await status_message.edit_text(
            f"🎬 **Procesando video**\n"
            f"📊 Audio extraído: {get_file_size(audio_file_path)}\n"
            f"🗜️ Comprimiendo audio para transcripción..."
        )

        await compress_audio(audio_file_path, compressed_file_path)
        logging.info(f"Audio compressed, size: {get_file_size(compressed_file_path)}")

        # Transcribe audio
        await status_message.edit_text(
            f"🎬 **Transcribiendo video**\n"
            f"📊 Audio comprimido: {get_file_size(compressed_file_path)}\n"
            f"🤖 Procesando con OpenAI Whisper...\n"
            f"⏳ Esto puede tomar unos momentos..."
        )

        logging.info("Starting transcription process")
        transcription = await transcribe_audio(compressed_file_path)
        logging.info(f"Transcription completed, length: {len(transcription)} chars")

        # Update with success
        await status_message.edit_text(
            f"🎬 **¡Transcripción completada!**\n"
            f"📊 {len(transcription):,} caracteres transcritos\n"
            f"⚡ Procesando resultado final..."
        )

        # Process transcription
        await process_media(message, transcription, message, content_type="video", status_message=status_message)

    except Exception as e:
        logging.error(f"Error processing video: {str(e)}", exc_info=True)
        try:
            # Delete status message and send error
            await status_message.delete()
            await message.reply_text(
                f"🎬 **Error procesando video**\n"
                f"❌ Error durante el procesamiento\n"
                f"🔧 Por favor, intenta nuevamente más tarde."
            )
        except Exception:
            # Fallback if status message can't be deleted
            await message.reply_text(
                "❌ Ocurrió un error al procesar la transcripción del video."
            )
        raise

    finally:
        # Cleanup temporary files
        for file_path in [temp_file_path, audio_file_path, compressed_file_path]:
            if file_path:
                try:
                    os.unlink(file_path)
                    logging.info(f"Removed temporary file: {file_path}")
                except Exception as e:
                    logging.error(
                        f"Error removing temporary file {file_path}: {str(e)}"
                    )
