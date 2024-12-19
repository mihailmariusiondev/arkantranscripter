import os
from dotenv import load_dotenv
from bot.utils.database import db


class BotConfig:
    def __init__(self):
        # Load environment variables from .env file, overriding existing variables
        load_dotenv(override=True)
        # Get API keys from environment variables
        self.bot_token = os.getenv("BOT_TOKEN")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    @property
    def auto_transcription_enabled(self) -> bool:
        return db.get_setting("auto_transcription_enabled")

    @property
    def enhanced_transcription_enabled(self) -> bool:
        return db.get_setting("enhanced_transcription_enabled")

    @property
    def output_text_file_enabled(self) -> bool:
        return db.get_setting("output_text_file_enabled")

    def toggle_auto_transcription(self):
        return db.toggle_setting("auto_transcription_enabled")

    def toggle_enhanced_transcription(self):
        return db.toggle_setting("enhanced_transcription_enabled")

    def toggle_output_text_file(self):
        return db.toggle_setting("output_text_file_enabled")


# Create a global instance of BotConfig
bot_config = BotConfig()
