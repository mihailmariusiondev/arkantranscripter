from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import logging
from config.bot_config import bot_config
from bot.utils.config_utils import get_current_config_status


async def config_callback_handler(update: Update, context: CallbackContext) -> None:
    """
    Handle callback queries from configuration inline buttons.
    """
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data

    logging.info(f"Config callback received from user {user_id}: {callback_data}")

    try:
        await query.answer()  # Acknowledge the callback query

        if callback_data == "toggle_auto_transcription":
            bot_config.toggle_auto_transcription()
            await update_config_message(query)

        elif callback_data == "toggle_enhanced_transcription":
            bot_config.toggle_enhanced_transcription()
            await update_config_message(query)

        elif callback_data == "toggle_output_text_file":
            bot_config.toggle_output_text_file()
            await update_config_message(query)

        elif callback_data == "change_transcription_speed":
            await show_speed_options(query)

        elif callback_data.startswith("set_speed_"):
            speed = int(callback_data.split("_")[-1])
            bot_config.set_transcription_speed(speed)
            await update_config_message(query)

        elif callback_data == "back_to_config":
            await update_config_message(query)

        elif callback_data == "close_config":
            await query.edit_message_text("✅ Configuración cerrada.")

        logging.info(f"Config callback processed successfully for user {user_id}")

    except Exception as e:
        logging.error(f"Error processing config callback for user {user_id}: {str(e)}", exc_info=True)
        await query.edit_message_text("❌ Error al procesar la configuración.")


async def update_config_message(query):
    """Update the configuration message with current settings."""
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

    await query.edit_message_text(
        config_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def show_speed_options(query):
    """Show speed selection options."""
    current_speed = bot_config.transcription_speed

    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅ ' if current_speed == 1 else ''}x1 (Normal)",
                callback_data="set_speed_1"
            )
        ],
        [
            InlineKeyboardButton(
                f"{'✅ ' if current_speed == 2 else ''}x2 (Rápido - Ahorra 50%)",
                callback_data="set_speed_2"
            )
        ],
        [
            InlineKeyboardButton(
                f"{'✅ ' if current_speed == 3 else ''}x3 (Muy rápido - Ahorra 66%)",
                callback_data="set_speed_3"
            )
        ],
        [
            InlineKeyboardButton("🔙 Volver", callback_data="back_to_config")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    speed_message = (
        "⚡ **Velocidad de Transcripción**\n\n"
        "Selecciona la velocidad de procesamiento:\n\n"
        "• **x1**: Velocidad normal\n"
        "• **x2**: 2x más rápido (ahorra ~50% en costos)\n"
        "• **x3**: 3x más rápido (ahorra ~66% en costos)\n\n"
        "⚠️ Velocidades mayores pueden afectar ligeramente la calidad."
    )

    await query.edit_message_text(
        speed_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )