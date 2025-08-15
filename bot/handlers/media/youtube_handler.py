from typing import Optional
from telegram import Update
from telegram.ext import CallbackContext
from bot.services.youtube_transcript_service import YouTubeTranscriptExtractor
from bot.utils.transcription_utils import extract_video_id, process_media
import logging
import asyncio


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

    # Send initial message with video ID info
    status_message = await update.message.chat.send_message(
        f"🎬 **Procesando video de YouTube**\n"
        f"📝 ID: `{video_id}`\n"
        f"🔄 Iniciando extracción con múltiples estrategias..."
    )

    try:
        # Initialize enhanced extractor with callback for status updates
        extractor = YouTubeTranscriptExtractor()

        # Create callback function to update user on progress
        async def status_callback(strategy_num, strategy_name, total_strategies, status, details=""):
            try:
                if status == "trying":
                    await status_message.edit_text(
                        f"🎬 **Procesando video de YouTube**\n"
                        f"📝 ID: `{video_id}`\n"
                        f"⚡ Estrategia {strategy_num}/{total_strategies}: **{strategy_name}**\n"
                        f"🔄 {details if details else 'Extrayendo transcripción...'}"
                    )
                elif status == "success":
                    await status_message.edit_text(
                        f"🎬 **Video de YouTube procesado**\n"
                        f"📝 ID: `{video_id}`\n"
                        f"✅ **Éxito con estrategia {strategy_num}**: {strategy_name}\n"
                        f"📊 {details if details else 'Transcripción obtenida correctamente'}\n"
                        f"🔄 Procesando transcripción..."
                    )
                elif status == "failed":
                    if strategy_num < total_strategies:
                        await status_message.edit_text(
                            f"🎬 **Procesando video de YouTube**\n"
                            f"📝 ID: `{video_id}`\n"
                            f"❌ Estrategia {strategy_num} falló: {strategy_name}\n"
                            f"🔄 Probando siguiente estrategia..."
                        )
                        # Small delay to show the failure message
                        await asyncio.sleep(0.5)
            except Exception as e:
                logging.warning(f"Error updating status message: {e}")

        # Extract transcript with status updates
        transcription = await extractor.extract_transcript_with_status(video_id, status_callback)

        if not transcription:
            logging.error(f"All transcript extraction methods failed for video {video_id}")
            await status_message.edit_text(
                f"🎬 **Error procesando video**\n"
                f"📝 ID: `{video_id}`\n"
                f"❌ **Todas las estrategias fallaron**\n"
                f"💡 El video podría no tener subtítulos o estar restringido geográficamente."
            )
            return

        logging.info(f"Transcription extracted successfully, length: {len(transcription)} chars")

        # Update status message with success
        await status_message.edit_text(
            f"🎬 **Transcripción obtenida exitosamente**\n"
            f"📝 ID: `{video_id}`\n"
            f"📊 Longitud: {len(transcription):,} caracteres\n"
            f"⚡ Procesando y mejorando transcripción..."
        )

        # Process the transcription with final status update
        await process_media(
            update.message, transcription, original_message, content_type="youtube", status_message=status_message
        )

        logging.info(f"Enhanced YouTube transcription completed for video {video_id}")

    except Exception as e:
        logging.error(f"Unexpected error processing YouTube video {video_id}: {str(e)}")
        try:
            # Delete status message and send error
            await status_message.delete()
            await update.message.chat.send_message(
                f"🎬 **Error procesando video de YouTube**\n"
                f"📝 ID: `{video_id}`\n"
                f"❌ Error durante el procesamiento\n"
                f"🔧 Por favor, intenta nuevamente más tarde."
            )
        except Exception:
            # Fallback if status message can't be deleted
            await update.message.chat.send_message(
                "❌ Ocurrió un error inesperado al procesar la transcripción."
            )
