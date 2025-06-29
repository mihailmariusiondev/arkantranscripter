from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import logging
from config.bot_config import bot_config
from bot.utils.config_utils import get_current_config_status


async def configure_handler(update: Update, context: CallbackContext) -> None:
    """
    Handle the /configure command by showing configuration menu with inline buttons.
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    logging.info(f"Configure command received from user {user_id} in chat {chat_id}")

    try:
        # Create inline keyboard with configuration options
        keyboard = [
            [
                InlineKeyboardButton(
                    f"🎯 Transcripción automática: {'ON' if bot_config.auto_transcription_enabled else 'OFF'}",
                    callback_data="toggle_auto_transcription"
                )
            ],
            [
                InlineKeyboardButton(
                    f"✨ Transcripción mejorada: {'ON' if bot_config.enhanced_transcription_enabled else 'OFF'}",
                    callback_data="toggle_enhanced_transcription"
                )
            ],
            [
                InlineKeyboardButton(
                    f"📄 Salida como archivo: {'ON' if bot_config.output_text_file_enabled else 'OFF'}",
                    callback_data="toggle_output_text_file"
                )
            ],
            [
                InlineKeyboardButton(
                    f"⚡ Velocidad: {bot_config.get_transcription_speed_text()}",
                    callback_data="change_transcription_speed"
                )
            ],
            [
                InlineKeyboardButton("❌ Cerrar", callback_data="close_config")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        config_message = (
            "⚙️ **Configuración del Bot**\n\n"
            f"{get_current_config_status()}\n"
            "Usa los botones de abajo para cambiar las configuraciones:"
        )

        await update.message.reply_text(
            config_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

        logging.info(f"Configuration menu sent to user {user_id}")

    except Exception as e:
        logging.error(
            f"Error showing configuration menu to user {user_id}: {str(e)}",
            exc_info=True
        )
        raise