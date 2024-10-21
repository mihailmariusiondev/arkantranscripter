import os
import json
from dotenv import load_dotenv

class BotConfig:
    # A class to manage the bot's configuration, including settings and API keys.
    # This class handles loading from environment variables and a JSON file,
    # as well as saving changes to the JSON file.

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        # Get API keys from environment variables
        self.bot_token = os.getenv("BOT_TOKEN")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        # Load other settings from JSON file
        self._load_settings()

    def _load_settings(self):
        # Load settings from the JSON file.
        # This includes feature toggles and authorized users.
        with open('config/bot_settings.json', 'r') as f:
            settings = json.load(f)
        self.auto_transcription_enabled = settings['auto_transcription_enabled']
        self.enhanced_transcription_enabled = settings['enhanced_transcription_enabled']
        self.authorized_users = set(settings['authorized_users'])
        self.output_text_file_enabled = settings.get('output_text_file_enabled', False)

    def _save_settings(self):
        # Save current settings to the JSON file.
        # This method is called after toggling any feature to persist changes.
        settings = {
            'auto_transcription_enabled': self.auto_transcription_enabled,
            'enhanced_transcription_enabled': self.enhanced_transcription_enabled,
            'authorized_users': list(self.authorized_users),
            'output_text_file_enabled': self.output_text_file_enabled
        }
        with open('config/bot_settings.json', 'w') as f:
            json.dump(settings, f, indent=4)

    def toggle_auto_transcription(self):
        # Toggle the auto transcription feature and save the new state.
        self.auto_transcription_enabled = not self.auto_transcription_enabled
        self._save_settings()

    def toggle_enhanced_transcription(self):
        # Toggle the enhanced transcription feature and save the new state.
        self.enhanced_transcription_enabled = not self.enhanced_transcription_enabled
        self._save_settings()

    def toggle_auto_summary(self):
        # Toggle the auto summary feature and save the new state.
        self.auto_summary_enabled = not self.auto_summary_enabled
        self._save_settings()

    def toggle_output_text_file(self):
        # Toggle the output to text file feature and save the new state.
        self.output_text_file_enabled = not self.output_text_file_enabled
        self._save_settings()

# Create a global instance of BotConfig
bot_config = BotConfig()
