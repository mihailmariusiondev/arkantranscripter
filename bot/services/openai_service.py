import logging
from openai import OpenAI
from config.bot_config import bot_config


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=bot_config.openai_api_key)

    async def transcribe_audio(self, file_path: str) -> str:
        """Transcribe an audio file using OpenAI's Whisper model."""
        try:
            with open(file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file
                )
            logging.info(f"Transcripción inicial completa:\n{transcription.text}")
            return transcription.text
        except Exception as e:
            logging.error(f"Error en la transcripción de audio: {e}")
            raise

    async def post_process_transcription(self, transcription: str) -> str:
        """Post-process the transcription using OpenAI's GPT model for minimal corrections."""
        try:
            logging.info(f"Transcripción original completa:\n{transcription[:50]}...")
            system_prompt = """You are a transcription improvement assistant. Your ONLY task is to make MINIMAL corrections to spelling, punctuation, and sentence structure WITHOUT changing ANY words or their order. Do NOT paraphrase, summarize, or alter the content in any way.
            Rules:
            1. Correct obvious spelling errors ONLY if you are 100% certain.
            2. Add or adjust punctuation ONLY where absolutely necessary for clarity.
            3. DO NOT change any words, even if they seem incorrect or informal.
            4. DO NOT add or remove any content.
            5. Maintain ALL original phrasing, slang, and informal language.
            6. If unsure about a correction, leave the original text as is.
            7. Preserve all original sentence breaks and paragraph structure."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcription},
                ],
                temperature=0.0,
            )
            improved_transcription = response.choices[0].message.content
            logging.info(
                f"Transcripción mejorada completa:\n{improved_transcription[:50]}..."
            )
            return improved_transcription
        except Exception as e:
            logging.error(f"Error en el post-procesamiento de la transcripción: {e}")
            raise


# Create a global instance of OpenAIService
openai_service = OpenAIService()
