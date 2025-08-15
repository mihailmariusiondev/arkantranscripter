import os
import aiohttp
import asyncio
from typing import Optional, List, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable
from youtube_transcript_api.proxies import WebshareProxyConfig, GenericProxyConfig
import logging
import random


class YouTubeTranscriptExtractor:
    """
    Enhanced YouTube transcript extractor with multiple service fallback.
    Implements robust geolocation bypass using multiple strategies.

    This is the centralized service used by both the bot handler and the comprehensive tests.
    """

    def __init__(self):
        self.strategies = [
            self._extract_with_savesubs,
            self._extract_with_youtube_transcript_io,
            self._extract_with_notegpt,
            self._extract_with_tactiq,
            self._extract_with_youtube_transcript_api_proxy,
            self._extract_with_youtube_transcript_api_direct,
        ]

        # Service configurations
        self.notegpt_config = {
            'url': 'https://notegpt.io/api/v2/video-transcript',
            'headers': {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9,es;q=0.8',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://notegpt.io/youtube-transcript-generator',
                'user-agent': self._get_random_user_agent(),
            }
        }

        self.tactiq_config = {
            'url': 'https://tactiq-apps-prod.tactiq.io/transcript',
            'headers': {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9,es;q=0.8',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'origin': 'https://tactiq.io',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://tactiq.io/',
                'user-agent': self._get_random_user_agent(),
            }
        }

        self.youtube_transcript_io_config = {
            'url': 'https://www.youtube-transcript.io/api/transcripts/v2',
            'headers': {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9,es;q=0.8',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'origin': 'https://www.youtube-transcript.io',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': self._get_random_user_agent(),
                'x-request-channel': '9527-c'
            }
        }

    def _get_random_user_agent(self) -> str:
        """Get a random user agent for request rotation."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0',
        ]
        return random.choice(user_agents)

    async def _extract_with_savesubs(self, video_id: str) -> Optional[str]:
        """
        Extract transcript using Savesubs.com service.
        This service provides transcript extraction for YouTube videos.
        """
        try:
            url = f'https://www.savesubs.com/api/subtitle/{video_id}'

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                headers = {
                    'accept': 'application/json, text/plain, */*',
                    'accept-language': 'en-US,en;q=0.9,es;q=0.8',
                    'referer': 'https://www.savesubs.com/',
                    'user-agent': self._get_random_user_agent(),
                }

                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Parse the response format
                        if isinstance(data, dict) and 'result' in data:
                            subtitle_tracks = data.get('result', [])

                            # Look for English subtitles first
                            for track in subtitle_tracks:
                                if track.get('language', '').lower() in ['en', 'english', 'en-us']:
                                    content = track.get('content', '')
                                    if content:
                                        # Clean up the content (remove timestamps, etc.)
                                        import re
                                        cleaned = re.sub(r'^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}$', '', content, flags=re.MULTILINE)
                                        cleaned = re.sub(r'^\d+$', '', cleaned, flags=re.MULTILINE)
                                        cleaned = '\n'.join(line.strip() for line in cleaned.split('\n') if line.strip())
                                        return cleaned

                            # If no English, try first available
                            if subtitle_tracks:
                                content = subtitle_tracks[0].get('content', '')
                                if content:
                                    import re
                                    cleaned = re.sub(r'^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}$', '', content, flags=re.MULTILINE)
                                    cleaned = re.sub(r'^\d+$', '', cleaned, flags=re.MULTILINE)
                                    cleaned = '\n'.join(line.strip() for line in cleaned.split('\n') if line.strip())
                                    return cleaned

                    logging.warning(f"Savesubs returned status {response.status} for video {video_id}")
                    return None

        except Exception as e:
            logging.warning(f"Savesubs extraction failed for video {video_id}: {str(e)}")
            return None

    async def _extract_with_youtube_transcript_io(self, video_id: str) -> Optional[str]:
        """
        Extract transcript using YouTube-Transcript.io service.
        This service requires authentication but provides high-quality transcript data.
        Note: This service uses temporary auth tokens that may expire.
        """
        try:
            payload = {"ids": [video_id]}
            timeout = aiohttp.ClientTimeout(total=10)  # Reduced timeout for faster testing

            # Note: This service requires authentication.
            # The token from the curl command is temporary and will expire.
            # For production use, you would need to implement proper token management.
            auth_headers = self.youtube_transcript_io_config['headers'].copy()

            # Try without auth first to see if the service works in some cases
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.youtube_transcript_io_config['url'],
                    json=payload,
                    headers=auth_headers
                ) as response:

                    if response.status == 401:
                        logging.warning("YouTube-Transcript.io: Authentication required (401). This service needs a valid auth token.")
                        return None

                    if response.status != 200:
                        logging.warning(f"YouTube-Transcript.io API returned status {response.status}")
                        return None

                    data = await response.json()

                    # Check if we have successful results
                    success_results = data.get('success', [])
                    if not success_results:
                        logging.warning("YouTube-Transcript.io: No successful results found")
                        return None

                    # Get the first successful result
                    result = success_results[0]
                    tracks = result.get('tracks', [])

                    if not tracks:
                        logging.warning("YouTube-Transcript.io: No transcript tracks found")
                        return None

                    # Get the first track (should be the main transcript)
                    track = tracks[0]
                    transcript_segments = track.get('transcript', [])

                    if not transcript_segments:
                        logging.warning("YouTube-Transcript.io: No transcript segments found")
                        return None

                    # Extract text from transcript segments
                    text_segments = []
                    for segment in transcript_segments:
                        text = segment.get('text', '').strip()
                        if text:
                            text_segments.append(text)

                    if text_segments:
                        transcript = ' '.join(text_segments)
                        logging.info(f"YouTube-Transcript.io: Successfully extracted {len(transcript)} chars")
                        return transcript

                    logging.warning("YouTube-Transcript.io: No valid text segments found")
                    return None

        except Exception as e:
            logging.error(f"YouTube-Transcript.io extraction failed: {str(e)}")
            return None

    async def _extract_with_notegpt(self, video_id: str) -> Optional[str]:
        """
        Extract transcript using NoteGPT service.
        This service appears to work reliably with geolocation restrictions.
        """
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            payload = {
                'platform': 'youtube',
                'video_id': video_id
            }

            timeout = aiohttp.ClientTimeout(total=10)  # Reduced timeout for faster testing

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    self.notegpt_config['url'],
                    params=payload,
                    headers=self.notegpt_config['headers']
                ) as response:

                    if response.status != 200:
                        logging.warning(f"NoteGPT API returned status {response.status}")
                        return None

                    data = await response.json()

                    if data.get('code') != 100000:
                        logging.warning(f"NoteGPT API error: {data.get('message', 'Unknown error')}")
                        return None

                    # Extract transcript from response
                    transcripts = data.get('data', {}).get('transcripts', {})

                    # Try English first, then auto-generated, then any available
                    for lang_code in ['en', 'en_auto']:
                        if lang_code in transcripts:
                            transcript_data = transcripts[lang_code]

                            # Try custom format first (longer segments), then default
                            for format_type in ['custom', 'default', 'auto']:
                                if format_type in transcript_data:
                                    segments = transcript_data[format_type]
                                    if segments:
                                        text = ' '.join([segment.get('text', '') for segment in segments])
                                        if text and text.strip() != 'No text':
                                            logging.info(f"NoteGPT: Successfully extracted {len(text)} chars using {lang_code}.{format_type}")
                                            return text.strip()

                    logging.warning("NoteGPT: No valid transcript data found")
                    return None

        except Exception as e:
            logging.error(f"NoteGPT extraction failed: {str(e)}")
            return None

    async def _extract_with_tactiq(self, video_id: str) -> Optional[str]:
        """
        Extract transcript using Tactiq service.
        Alternative service for geolocation bypass.
        """
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            payload = {
                'videoUrl': youtube_url,
                'langCode': 'en'
            }

            timeout = aiohttp.ClientTimeout(total=10)  # Reduced timeout for faster testing

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.tactiq_config['url'],
                    json=payload,
                    headers=self.tactiq_config['headers']
                ) as response:

                    if response.status != 200:
                        logging.warning(f"Tactiq API returned status {response.status}")
                        return None

                    data = await response.json()

                    # Extract captions from response
                    captions = data.get('captions', [])
                    if not captions:
                        logging.warning("Tactiq: No captions found in response")
                        return None

                    # Filter out "No text" entries and combine
                    text_segments = []
                    for caption in captions:
                        text = caption.get('text', '').strip()
                        if text and text != 'No text':
                            text_segments.append(text)

                    if text_segments:
                        transcript = ' '.join(text_segments)
                        logging.info(f"Tactiq: Successfully extracted {len(transcript)} chars")
                        return transcript

                    logging.warning("Tactiq: No valid text segments found")
                    return None

        except Exception as e:
            logging.error(f"Tactiq extraction failed: {str(e)}")
            return None

    async def _extract_with_youtube_transcript_api_proxy(self, video_id: str) -> Optional[str]:
        """
        Extract using YouTubeTranscriptApi with proxy configuration.
        Uses the current proxy setup as fallback.
        """
        try:
            # Initialize with proxy configuration if available
            proxy_config = None

            if os.getenv("WEBSHARE_USERNAME") and os.getenv("WEBSHARE_PASSWORD"):
                proxy_config = WebshareProxyConfig(
                    proxy_username=os.getenv("WEBSHARE_USERNAME"),
                    proxy_password=os.getenv("WEBSHARE_PASSWORD"),
                    filter_ip_locations=["us", "ca", "gb", "de", "fr", "nl", "sg", "au"],
                )
            elif os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY"):
                proxy_config = GenericProxyConfig(
                    http_url=os.getenv("HTTP_PROXY", ""),
                    https_url=os.getenv("HTTPS_PROXY", ""),
                )

            ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)

            # Get available transcripts
            transcript_list = ytt_api.list(video_id)

            # Try to get English transcript first, fall back to first available
            transcript = next(
                (t for t in transcript_list if t.language_code in ["en", "en-US"]),
                next(iter(transcript_list), None),
            )

            if not transcript:
                return None

            # Fetch transcript
            fetched_transcript = transcript.fetch()
            text = " ".join([entry.text for entry in fetched_transcript])

            logging.info(f"YouTube Transcript API (proxy): Successfully extracted {len(text)} chars")
            return text

        except (NoTranscriptFound, VideoUnavailable) as e:
            logging.warning(f"YouTube Transcript API (proxy): {str(e)}")
            return None
        except Exception as e:
            logging.error(f"YouTube Transcript API (proxy) failed: {str(e)}")
            return None

    async def _extract_with_youtube_transcript_api_direct(self, video_id: str) -> Optional[str]:
        """
        Extract using YouTubeTranscriptApi without proxy as last resort.
        """
        try:
            ytt_api = YouTubeTranscriptApi()

            # Get available transcripts
            transcript_list = ytt_api.list(video_id)

            # Try to get English transcript first, fall back to first available
            transcript = next(
                (t for t in transcript_list if t.language_code in ["en", "en-US"]),
                next(iter(transcript_list), None),
            )

            if not transcript:
                return None

            # Fetch transcript
            fetched_transcript = transcript.fetch()
            text = " ".join([entry.text for entry in fetched_transcript])

            logging.info(f"YouTube Transcript API (direct): Successfully extracted {len(text)} chars")
            return text

        except (NoTranscriptFound, VideoUnavailable) as e:
            logging.warning(f"YouTube Transcript API (direct): {str(e)}")
            return None
        except Exception as e:
            logging.error(f"YouTube Transcript API (direct) failed: {str(e)}")
            return None

    async def extract_transcript(self, video_id: str) -> Optional[str]:
        """
        Extract transcript using all available strategies with fallback.

        Args:
            video_id: YouTube video ID

        Returns:
            Extracted transcript text or None if all strategies fail
        """
        logging.info(f"Starting transcript extraction for video {video_id}")

        for i, strategy in enumerate(self.strategies, 1):
            try:
                logging.info(f"Trying strategy {i}/{len(self.strategies)}: {strategy.__name__}")

                # Add delay between attempts to avoid rate limiting
                if i > 1:
                    delay = random.uniform(0.5, 1.5)  # Reduced delay for faster testing
                    logging.info(f"Waiting {delay:.1f}s before next strategy...")
                    await asyncio.sleep(delay)

                result = await strategy(video_id)

                if result and len(result.strip()) > 0:
                    logging.info(f"Success with strategy {i}: {strategy.__name__}")
                    return result

                logging.warning(f"Strategy {i} ({strategy.__name__}) returned no content")

            except Exception as e:
                logging.error(f"Strategy {i} ({strategy.__name__}) failed: {str(e)}")
                continue

        logging.error(f"All extraction strategies failed for video {video_id}")
        return None

    def get_strategy_methods(self) -> Dict[str, callable]:
        """
        Get a dictionary of strategy methods for testing purposes.

        Returns:
            Dictionary mapping strategy names to their methods
        """
        return {
            'savesubs': self._extract_with_savesubs,
            'youtube_transcript_io': self._extract_with_youtube_transcript_io,
            'notegpt': self._extract_with_notegpt,
            'tactiq': self._extract_with_tactiq,
            'youtube_api_proxy': self._extract_with_youtube_transcript_api_proxy,
            'youtube_api_direct': self._extract_with_youtube_transcript_api_direct
        }

    def get_strategy_names(self) -> List[str]:
        """
        Get a list of all available strategy names.

        Returns:
            List of strategy names
        """
        return list(self.get_strategy_methods().keys())
