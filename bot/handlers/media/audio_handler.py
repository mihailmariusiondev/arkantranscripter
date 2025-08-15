from telegram import Message
from telegram.ext import CallbackContext
from bot.utils.transcription_utils import (
    transcribe_audio,
    process_media,
    compress_audio,
    get_file_size,
)
from config.constants import MAX_FILE_SIZE
import tempfile
import os
import mimetypes
import logging


async def audio_handler(message: Message, context: CallbackContext) -> None:
    """
    Handle audio and voice message transcription requests.

    Args:
        message: Telegram message containing audio/voice
        context: Callback context
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Determine file details based on message type
    is_audio = bool(message.audio)
    file_id = message.audio.file_id if is_audio else message.voice.file_id
    file_size = message.audio.file_size if is_audio else message.voice.file_size

    logging.info(
        f"Processing {'audio' if is_audio else 'voice'} message from user {user_id}, file_id: {file_id}"
    )
    logging.info(f"File size: {file_size} bytes")

    # Check file size limit
    if file_size > MAX_FILE_SIZE:
        logging.warning(f"File size {file_size} exceeds limit of {MAX_FILE_SIZE} bytes")
        await message.chat.send_message(
            f"🎵 **Audio demasiado grande**\n"
            f"📊 Tamaño: {file_size/1024/1024:.1f} MB\n"
            f"⚠️ Límite máximo: {MAX_FILE_SIZE/1024/1024:.0f} MB\n"
            f"💡 Por favor, envía un archivo más pequeño."
        )
        return

    # Send initial status message
    content_type = "audio" if is_audio else "mensaje de voz"
    status_message = await message.chat.send_message(
        f"🎵 **Procesando {content_type}**\n"
        f"📊 Tamaño: {file_size/1024/1024:.1f} MB\n"
        f"🔄 Descargando archivo..."
    )

    try:
        # Get file from Telegram
        file = await context.bot.get_file(file_id)
        logging.info(f"Retrieved file info: {file.file_path}")

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
        temp_file_path = temp_file.name
        temp_file.close()
        logging.info(f"Created temporary file: {temp_file_path}")

        try:
            # Download audio file
            await status_message.edit_text(
                f"🎵 **Procesando {content_type}**\n"
                f"📊 Tamaño: {file_size/1024/1024:.1f} MB\n"
                f"⬇️ Descargando archivo de Telegram..."
            )

            await file.download_to_drive(custom_path=temp_file_path)
            logging.info(
                f"Audio downloaded successfully, size: {get_file_size(temp_file_path)}"
            )

            # Compress audio
            await status_message.edit_text(
                f"🎵 **Procesando {content_type}**\n"
                f"📊 Archivo descargado: {get_file_size(temp_file_path)}\n"
                f"🗜️ Comprimiendo audio para transcripción..."
            )

            compressed_file_path = tempfile.NamedTemporaryFile(
                delete=False, suffix=".ogg"
            ).name
            await compress_audio(temp_file_path, compressed_file_path)
            logging.info(
                f"Audio compressed, new size: {get_file_size(compressed_file_path)}"
            )

            # Transcribe audio
            await status_message.edit_text(
                f"🎵 **Transcribiendo {content_type}**\n"
                f"📊 Audio comprimido: {get_file_size(compressed_file_path)}\n"
                f"🤖 Procesando con OpenAI Whisper...\n"
                f"⏳ Esto puede tomar unos momentos..."
            )

            logging.info("Starting transcription process")
            transcription = await transcribe_audio(compressed_file_path)
            logging.info(f"Transcription completed, length: {len(transcription)} chars")

            # Update with success
            await status_message.edit_text(
                f"🎵 **¡Transcripción completada!**\n"
                f"📊 {len(transcription):,} caracteres transcritos\n"
                f"⚡ Procesando resultado final..."
            )

            # Process transcription
            await process_media(message, transcription, message, content_type="audio", status_message=status_message)

        except Exception as e:
            logging.error(f"Error processing audio file: {str(e)}", exc_info=True)
            try:
                # Delete status message and send error
                await status_message.delete()
                await message.reply_text(
                    f"🎵 **Error procesando {content_type}**\n"
                    f"❌ Error durante el procesamiento\n"
                    f"🔧 Por favor, intenta nuevamente más tarde."
                )
            except Exception:
                # Fallback if status message can't be deleted
                await message.reply_text(
                    "❌ Ocurrió un error al procesar la transcripción del audio."
                )
            raise

        finally:
            # Cleanup temporary files
            for file_path in [temp_file_path, compressed_file_path]:
                try:
                    os.unlink(file_path)
                    logging.info(f"Removed temporary file: {file_path}")
                except Exception as e:
                    logging.error(
                        f"Error removing temporary file {file_path}: {str(e)}"
                    )

    except Exception as e:
        logging.error(f"Error in audio handler: {str(e)}", exc_info=True)
        raise
