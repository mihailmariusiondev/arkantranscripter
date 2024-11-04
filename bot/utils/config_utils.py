from bot.utils.database import db

def get_current_config_status():
    autotranscription_status = "ACTIVADO" if db.get_setting('auto_transcription_enabled') else "DESACTIVADO"
    enhanced_transcription_status = "ACTIVADO" if db.get_setting('enhanced_transcription_enabled') else "DESACTIVADO"
    output_text_file_status = "ACTIVADO" if db.get_setting('output_text_file_enabled') else "DESACTIVADO"
    auto_summarize_status = "ACTIVADO" if db.get_setting('auto_summarize_enabled') else "DESACTIVADO"

    return (
        f"Estado actual de las funciones:\n"
        f"Autotranscripción: {autotranscription_status}\n"
        f"Transcripción mejorada: {enhanced_transcription_status}\n"
        f"Salida en archivo de texto: {output_text_file_status}\n"
        f"Resumen automático: {auto_summarize_status}\n"
    )
