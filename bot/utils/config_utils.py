from bot.utils.database import db
from config.bot_config import bot_config


def get_current_config_status():
    autotranscription_status = (
        "ACTIVADO" if db.get_setting("auto_transcription_enabled") else "DESACTIVADO"
    )
    enhanced_transcription_status = (
        "ACTIVADO"
        if db.get_setting("enhanced_transcription_enabled")
        else "DESACTIVADO"
    )
    output_text_file_status = (
        "ACTIVADO" if db.get_setting("output_text_file_enabled") else "DESACTIVADO"
    )
    transcription_speed = bot_config.get_transcription_speed_text()

    return (
        f"Estado actual de las funciones:\n"
        f"Autotranscripción: {autotranscription_status}\n"
        f"Transcripción mejorada: {enhanced_transcription_status}\n"
        f"Salida en archivo de texto: {output_text_file_status}\n"
        f"Velocidad de transcripción: {transcription_speed}\n"
    )
