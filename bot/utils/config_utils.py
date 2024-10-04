from config.bot_config import bot_config

def get_current_config_status():
    autotranscription_status = "ACTIVADO" if bot_config.auto_transcription_enabled else "DESACTIVADO"
    enhanced_transcription_status = "ACTIVADO" if bot_config.enhanced_transcription_enabled else "DESACTIVADO"
    auto_summary_status = "ACTIVADO" if bot_config.auto_summary_enabled else "DESACTIVADO"

    return (
        f"Estado actual de las funciones:\n"
        f"Autotranscripción: {autotranscription_status}\n"
        f"Transcripción mejorada: {enhanced_transcription_status}\n"
        f"Resumen automático: {auto_summary_status}"
    )