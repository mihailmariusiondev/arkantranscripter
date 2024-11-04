import logging
from openai import OpenAI
from config.bot_config import bot_config


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=bot_config.openai_api_key)
        self.SUMMARY_PROMPTS = {
            'youtube': """You are a YouTube content summarizer specialized in long-form video content. Create a comprehensive summary that captures the essence of the video. Follow these rules:

            1. Length: Aim for 30-40% of original length for detailed coverage
            2. Structure:
               - Lead with the main topic/thesis
               - Maintain the video's logical flow
               - Include key timestamps or sections if mentioned
            3. Content:
               - Preserve important statistics and data
               - Include relevant quotes or key statements
               - Maintain the original tone (educational, news, etc.)
               - Highlight main arguments or conclusions
            4. Format:
               "📝 RESUMEN DE VIDEO DE YOUTUBE:

               📍 TEMA PRINCIPAL:
               [main topic/thesis]

               📊 PUNTOS CLAVE:
               [key points and data]

               📝 DESARROLLO:
               [detailed content]

               🔍 CONCLUSIONES:
               [main takeaways/conclusions]"
            """,

            'video': """You are a direct video content summarizer. Create a summary that captures both visual and spoken content. Follow these rules:

            1. Length: Aim for 50-60% of original length
            2. Focus:
               - Capture main message and context
               - Include relevant visual elements mentioned
               - Preserve important details and instructions
            3. Content:
               - Maintain chronological order
               - Include key demonstrations or actions
               - Preserve specific instructions if present
            4. Format:
               "📝 RESUMEN DE VIDEO:
               [comprehensive summary including context and key points]"
            """,

            'audio': """You are an audio content summarizer. Create a clear summary of spoken content. Follow these rules:

            1. Length: Aim for 50-60% of original length
            2. Focus:
               - Capture main message and intent
               - Preserve important context
               - Include key details and specifics
            3. Content:
               - Maintain speaker's main points
               - Include time-sensitive information
               - Preserve important quotes or statements
            4. Format:
               "📝 RESUMEN DE AUDIO:
               [clear summary of the audio content]"
            """
        }

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

    async def summarize_transcription(self, transcription: str, content_type: str) -> str:
        """Create a summary based on handler type."""
        try:
            if content_type not in self.SUMMARY_PROMPTS:
                logging.warning(f"Unknown content type: {content_type}, defaulting to 'video'")
                content_type = 'video'

            system_prompt = self.SUMMARY_PROMPTS[content_type]

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcription},
                ],
                temperature=0.3,
            )
            summary = response.choices[0].message.content
            logging.info(f"Summary generated for {content_type}, length: {len(summary)} chars")
            return summary
        except Exception as e:
            logging.error(f"Error generating summary: {e}")
            raise


# Create a global instance of OpenAIService
openai_service = OpenAIService()
