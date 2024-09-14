import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN, auto_transcription_enabled
from handlers import start, transcribe, toggle_autotranscription, handle_message

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("transcribe", transcribe))
    application.add_handler(CommandHandler("toggle_autotranscription", toggle_autotranscription))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info(f"Iniciando el bot con transcripción automática {'activada' if auto_transcription_enabled else 'desactivada'}")

    application.run_polling()
