import logging
from openai import OpenAI
from config.bot_config import bot_config
import os


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=bot_config.openai_api_key)

    async def transcribe_audio(self, file_path: str) -> str:
        """
        Transcribe an audio file using OpenAI's Whisper model.

        Args:
            file_path: Path to the audio file to transcribe

        Returns:
            str: The transcribed text
        """
        try:
            logging.info(f"Starting audio transcription for file: {file_path}")
            file_size = os.path.getsize(file_path)
            logging.info(f"File size: {file_size} bytes")

            with open(file_path, "rb") as audio_file:
                logging.info("Sending request to OpenAI Whisper API")
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file
                )

            logging.info(
                f"Transcription completed successfully, length: {len(transcription.text)} chars"
            )
            return transcription.text

        except Exception as e:
            logging.error(f"Error in audio transcription: {str(e)}", exc_info=True)
            raise

    async def post_process_transcription(self, transcription: str) -> str:
        """
        Post-process transcription using GPT model for improved quality.

        Args:
            transcription: Raw transcription text to enhance

        Returns:
            str: Enhanced transcription text
        """
        try:
            logging.info("Starting transcription post-processing")
            logging.info(f"Original transcription length: {len(transcription)} chars")

            system_prompt = """You are a transcription improvement assistant. Your ONLY task is to make MINIMAL corrections to spelling, punctuation, and sentence structure WITHOUT changing ANY words or their order. Do NOT paraphrase, summarize, or alter the content in any way.
            Rules:
            1. Correct obvious spelling errors ONLY if you are 100% certain.
            2. Add or adjust punctuation ONLY where absolutely necessary for clarity.
            3. DO NOT change any words, even if they seem incorrect or informal.
            4. DO NOT add or remove any content.
            5. Maintain ALL original phrasing, slang, and informal language.
            6. If unsure about a correction, leave the original text as is.
            7. Preserve all original sentence breaks and paragraph structure."""

            logging.info("Sending request to GPT model")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcription},
                ],
                temperature=0.0,
            )

            improved_text = response.choices[0].message.content
            logging.info(
                f"Post-processing complete, new length: {len(improved_text)} chars"
            )
            return improved_text

        except Exception as e:
            logging.error(
                f"Error in transcription post-processing: {str(e)}", exc_info=True
            )
            raise


# Create a global instance of OpenAIService
openai_service = OpenAIService()
