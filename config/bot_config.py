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
        # Load authorized users from environment variable
        self.authorized_users = os.getenv("AUTHORIZED_USERS", "").split(",")

    @property
    def auto_transcription_enabled(self) -> bool:
        return db.get_setting("auto_transcription_enabled")

    @property
    def enhanced_transcription_enabled(self) -> bool:
        return db.get_setting("enhanced_transcription_enabled")

    @property
    def output_text_file_enabled(self) -> bool:
        return db.get_setting("output_text_file_enabled")

    @property
    def transcription_speed(self) -> int:
        return db.get_int_setting("transcription_speed")

    def toggle_auto_transcription(self):
        return db.toggle_setting("auto_transcription_enabled")

    def toggle_enhanced_transcription(self):
        return db.toggle_setting("enhanced_transcription_enabled")

    def toggle_output_text_file(self):
        return db.toggle_setting("output_text_file_enabled")

    def set_transcription_speed(self, speed: int):
        if speed in [1, 2, 3]:
            db.set_int_setting("transcription_speed", speed)
            return speed
        else:
            raise ValueError("Speed must be 1, 2, or 3")

    def get_transcription_speed_text(self) -> str:
        speed = self.transcription_speed
        return f"x{speed}"


# Create a global instance of BotConfig
bot_config = BotConfig()

# Add authorized users from environment variable to the database
for user_id in bot_config.authorized_users:
    db.add_authorized_user(user_id)
