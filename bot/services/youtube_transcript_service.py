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
            self._extract_with_kome_ai,
            self._extract_with_anthiago,
            self._extract_with_yescribe,
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
                'x-request-channel': '9527-c',
                # Note: This service requires auth token and x-is-human validation
                # These are temporary tokens that expire, for production use implement proper token management
                'x-is-human': '{"b":1,"v":0.42819296923618766,"e":"eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..wgW4PDlDfMal0XWE.gKRMnlvi387tqetoqen8UwQ1lesPiYhqQQYLSaMyB-5yRQN2mtUjYZQOfGFwR4rR_W-N0qiUBWuFVDf_HwxQEabFXkOgaqgw8W4t0Puk-H-9fRRhVGrAhiufuZ5cvHYk38IbbbPWoj-CqRo2VcK-NK0JhIJvWo5i73pu_9AFzMfTHqaOai7rBiVOzsjkv08ffIqKtDcHxzwoeDuEqfnUbkANr0HlkXsogIsmrUzLcmI09YNUwteHFmVE_BYiYpxsuqb3SpuCZYhOReBDZEUL6bb7k7g4TmaGwJyf7D5GJcQqTVbbDnIDRsIvbfVhiUfsAfabEMo_uZ7q_3iIrpPYsmg9_8DJ5z_tejJxzZDvWDBq_cvJD0IPE-DfBkfDiuZNrvNvGbWPZn6xIqj--wLG-NU02Q_EL6d9IwEp--aHbdG99Bg92oUNN6vAPMokvlGIjQ1sHAeXGVb357pmeYEytlq9ddb6XyGHb_0Ak1SfaGxjiQY7nBdaHEee-wIjTZuklco9VQ.3eOD_PnL7skK2MdQPi03Pw","s":"kEbjZ0J4GBKh1mjK6ANHaNVFC7Cvyxu6CdBPef0da2oqitFS3Wqm3LjgJbjBFLPHR0bETYi93sOFOt54Bbiq9z069RTNYyr9NqpSikYwhXyWeNPfyjiojVKs9vXEMtnQjDUcKAtPH4cwCp9SdZjHsU5YZ1+koMQMdbv6V3x6Q9B1l37ADjg/ua9zDjNCAJS7JrwzaGaIQBZCnWBahPyJiLQaq1mncPQ5FCCl9dA8LKWHdVgCODNvtwD0Tq3ENbyFe/IA6AEny071ircJL3J7nk1HnlR5hGcWvVd6bTZC5byI0Hwmom8ozlgoXsWuLxEK","d":0,"vr":"1"}'
            }
        }

        self.kome_ai_config = {
            'url': 'https://kome.ai/api/transcript',
            'headers': {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9,es;q=0.8',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'origin': 'https://kome.ai',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://kome.ai/tools/youtube-transcript-generator',
                'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': self._get_random_user_agent(),
            }
        }

        self.anthiago_config = {
            'url': 'https://apiv2.anthiago.com/transcript',
            'headers': {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9,es;q=0.8',
                'cache-control': 'no-cache',
                'origin': 'https://anthiago.com',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://anthiago.com/',
                'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': self._get_random_user_agent(),
            },
            'cookies': {
                'user_login': 'false'
            }
        }

        self.yescribe_config = {
            'url': 'https://yescribe.erweima.ai/api/v1/yescribe/record/getVideoDetail',
            'headers': {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9,es;q=0.8',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'origin': 'https://yescribe.ai',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://yescribe.ai/',
                'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'uniqueid': '853d6904c0bb3bf143145a41dd2d6e82',
                'user-agent': self._get_random_user_agent(),
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
        This service provides high-quality transcript data with enhanced features.

        The service uses temporary auth tokens and human validation headers.
        For production use, implement proper token refresh mechanisms.
        """
        try:
            payload = {"ids": [video_id]}
            timeout = aiohttp.ClientTimeout(total=15)  # Increased timeout for this specific service

            # Prepare headers - clone config to avoid modifying the original
            headers = self.youtube_transcript_io_config['headers'].copy()

            # Try to get auth token from environment variable first
            auth_token = os.getenv("YOUTUBE_TRANSCRIPT_IO_TOKEN")
            if auth_token:
                headers['authorization'] = f'Bearer {auth_token}'
                logging.info("Using auth token from environment variable")
            else:
                # Fallback to the provided token (this will expire)
                fallback_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjU3YmZiMmExMWRkZmZjMGFkMmU2ODE0YzY4NzYzYjhjNjg3NTgxZDgiLCJ0eXAiOiJKV1QifQ.eyJwcm92aWRlcl9pZCI6ImFub255bW91cyIsImlzcyI6Imh0dHBzOi8vc2VjdXJldG9rZW4uZ29vZ2xlLmNvbS90cmFuc2NyaXB0LWZjNTgxIiwiYXVkIjoidHJhbnNjcmlwdC1mYzU4MSIsImF1dGhfdGltZSI6MTc1NTI1NzU3MywidXNlcl9pZCI6IncwRlo5MnZCOFNNYzhNb3BHUGMxWENFTjNHSTIiLCJzdWIiOiJ3MEZaOTJ2QjhTTWM4TW9wR1BjMVhDRU4zR0kyIiwiaWF0IjoxNzU1MjYyNDgxLCJleHAiOjE3NTUyNjYwODEsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnt9LCJzaWduX2luX3Byb3ZpZGVyIjoiYW5vbnltb3VzIn19.FEjrMnRL5YlZzRGOKi-pTykcx0VrtscbzXqgoxuGBxYTnHfRCT9kxkwe4Z6_3bO-I86VMoEcXwoseexhbMLyhjI4dObQ0P4iHzW3NS5EW2pHRDExRR6fIZ3-eMI8om-myhOeV4OIhcqPbdQ0KqX2GMs8BtwPOIscXxB5rd3rG17oTIBCSfuj6DMiYLuLBr9_xPHm9vKdi_Tn6SJ0RCsggwZsytpUMQHLIzM-VfqFr9arcEidMd-VOBEzr1sVDn2NBRwg3SWa7KMHx0hnG7MUZt4srD4FkcsvRH1OKFTmWlBQODEjFr5_CNGRd2m2dAjzSwzUwPkco_CSJcZ0jHYxYA"
                headers['authorization'] = f'Bearer {fallback_token}'
                logging.warning("Using fallback auth token - this may expire soon")

            # Add referer header specific to the video being processed
            headers['referer'] = f'https://www.youtube-transcript.io/videos?id={video_id}'

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.youtube_transcript_io_config['url'],
                    json=payload,
                    headers=headers
                ) as response:

                    if response.status == 401:
                        logging.warning("YouTube-Transcript.io: Authentication failed (401). Token may be expired.")
                        return None

                    if response.status == 403:
                        logging.warning("YouTube-Transcript.io: Access forbidden (403). May need valid x-is-human validation.")
                        return None

                    if response.status != 200:
                        response_text = await response.text()
                        logging.warning(f"YouTube-Transcript.io API returned status {response.status}: {response_text}")
                        return None

                    try:
                        data = await response.json()
                    except Exception as json_error:
                        logging.error(f"Failed to parse YouTube-Transcript.io response as JSON: {json_error}")
                        return None

                    # Check if we have successful results
                    success_results = data.get('success', [])
                    if not success_results:
                        failed_results = data.get('failed', [])
                        if failed_results:
                            logging.warning(f"YouTube-Transcript.io: Video processing failed: {failed_results}")
                        else:
                            logging.warning("YouTube-Transcript.io: No successful results and no failed results")
                        return None

                    # Get the first successful result
                    result = success_results[0]
                    tracks = result.get('tracks', [])

                    if not tracks:
                        logging.warning("YouTube-Transcript.io: No transcript tracks found")
                        return None

                    # Get the best available track (prefer first language available)
                    track = tracks[0]
                    transcript_segments = track.get('transcript', [])

                    if not transcript_segments:
                        logging.warning("YouTube-Transcript.io: No transcript segments found")
                        return None

                    # Extract text from transcript segments with timing information
                    text_segments = []
                    for segment in transcript_segments:
                        text = segment.get('text', '').strip()
                        if text:
                            text_segments.append(text)

                    if text_segments:
                        transcript = ' '.join(text_segments)

                        # Get additional metadata if available
                        title = result.get('title', 'Unknown')
                        microformat = result.get('microformat', {})
                        duration = microformat.get('playerMicroformatRenderer', {}).get('lengthSeconds', 'Unknown')

                        logging.info(f"YouTube-Transcript.io: Successfully extracted {len(transcript)} chars from '{title}' (duration: {duration}s)")
                        logging.info(f"YouTube-Transcript.io: Track language: {track.get('language', 'unknown')}")

                        return transcript

                    logging.warning("YouTube-Transcript.io: No valid text segments found")
                    return None

        except asyncio.TimeoutError:
            logging.error("YouTube-Transcript.io: Request timed out")
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

    async def _extract_with_kome_ai(self, video_id: str) -> Optional[str]:
        """
        Extract transcript using Kome.ai service.
        This service provides clean transcript extraction with duration info.
        """
        try:
            youtube_url = f"https://youtu.be/{video_id}"
            payload = {
                'video_id': f"{youtube_url}++0",
                'format': True
            }

            timeout = aiohttp.ClientTimeout(total=15)  # Increased timeout for this service

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.kome_ai_config['url'],
                    json=payload,
                    headers=self.kome_ai_config['headers']
                ) as response:

                    if response.status != 200:
                        response_text = await response.text()
                        logging.warning(f"Kome.ai API returned status {response.status}: {response_text}")
                        return None

                    try:
                        data = await response.json()
                    except Exception as json_error:
                        logging.error(f"Failed to parse Kome.ai response as JSON: {json_error}")
                        return None

                    # Extract transcript from response
                    transcript = data.get('transcript', '').strip()

                    if not transcript:
                        logging.warning("Kome.ai: No transcript found in response")
                        return None

                    # Get additional metadata if available
                    length = data.get('length', 'Unknown')
                    has_more = data.get('hasMore', False)

                    logging.info(f"Kome.ai: Successfully extracted {len(transcript)} chars (length: {length}, has_more: {has_more})")

                    return transcript

        except asyncio.TimeoutError:
            logging.error("Kome.ai: Request timed out")
            return None
        except Exception as e:
            logging.error(f"Kome.ai extraction failed: {str(e)}")
            return None

    async def _extract_with_anthiago(self, video_id: str) -> Optional[str]:
        """
        Extract transcript using Anthiago API service.
        This service provides clean subtitle extraction with timestamp info.
        """
        try:
            # Construct YouTube URL and API request
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"

            # Build query parameters
            params = {
                'get_video': youtube_url,
                'codeL': 'en',
                'status': 'false'
            }

            timeout = aiohttp.ClientTimeout(total=15)  # Increased timeout for this service

            # Prepare cookies
            cookies = aiohttp.CookieJar()
            for name, value in self.anthiago_config['cookies'].items():
                cookies.update_cookies({name: value})

            async with aiohttp.ClientSession(timeout=timeout, cookie_jar=cookies) as session:
                async with session.get(
                    self.anthiago_config['url'],
                    params=params,
                    headers=self.anthiago_config['headers']
                ) as response:

                    if response.status != 200:
                        response_text = await response.text()
                        logging.warning(f"Anthiago API returned status {response.status}: {response_text}")
                        return None

                    try:
                        data = await response.json()
                    except Exception as json_error:
                        logging.error(f"Failed to parse Anthiago response as JSON: {json_error}")
                        return None

                    # Check API response status
                    if data.get('status') != 'ok':
                        logging.warning(f"Anthiago API returned error status: {data.get('status')}")
                        return None

                    # Extract subtitles from response
                    subtitles = data.get('subtitles', [])

                    if not subtitles:
                        logging.warning("Anthiago: No subtitles found in response")
                        return None

                    # Process subtitles and combine text
                    text_segments = []
                    for subtitle in subtitles:
                        text = subtitle.get('f', '').strip()
                        if text:
                            # Decode HTML entities like &gt; and &#39;
                            import html
                            text = html.unescape(text)
                            text_segments.append(text)

                    if text_segments:
                        transcript = ' '.join(text_segments)

                        # Get additional metadata if available
                        title = data.get('title', 'Unknown')
                        url_base = data.get('urlBase', '')
                        premium = data.get('premium', False)

                        logging.info(f"Anthiago: Successfully extracted {len(transcript)} chars from '{title}' (premium: {premium})")

                        return transcript

                    logging.warning("Anthiago: No valid text segments found")
                    return None

        except asyncio.TimeoutError:
            logging.error("Anthiago: Request timed out")
            return None
        except Exception as e:
            logging.error(f"Anthiago extraction failed: {str(e)}")
            return None

    async def _extract_with_yescribe(self, video_id: str) -> Optional[str]:
        """
        Extract transcript using YeScribe API service.
        This service provides detailed transcript data with timestamps.
        """
        try:
            # Construct YouTube URL for the API
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"

            # Prepare JSON payload
            payload = {
                'videoUrl': youtube_url
            }

            timeout = aiohttp.ClientTimeout(total=20)  # Increased timeout for this service

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.yescribe_config['url'],
                    json=payload,
                    headers=self.yescribe_config['headers']
                ) as response:

                    if response.status != 200:
                        response_text = await response.text()
                        logging.warning(f"YeScribe API returned status {response.status}: {response_text}")
                        return None

                    try:
                        data = await response.json()
                    except Exception as json_error:
                        logging.error(f"Failed to parse YeScribe response as JSON: {json_error}")
                        return None

                    # Check API response code
                    if data.get('code') != 200:
                        msg = data.get('msg', 'Unknown error')
                        logging.warning(f"YeScribe API returned error: {msg}")
                        return None

                    # Extract data from response
                    response_data = data.get('data', {})

                    if not response_data:
                        logging.warning("YeScribe: No data found in response")
                        return None

                    # Extract transcript segments
                    transcript_segments = response_data.get('tranScript', [])

                    if not transcript_segments:
                        logging.warning("YeScribe: No transcript segments found")
                        return None

                    # Process transcript segments and combine text
                    text_segments = []
                    for segment in transcript_segments:
                        text = segment.get('text', '').strip()
                        if text:
                            text_segments.append(text)

                    if text_segments:
                        transcript = ' '.join(text_segments)

                        # Get additional metadata
                        title = response_data.get('title', 'Unknown')
                        author = response_data.get('author', 'Unknown')
                        length = response_data.get('length', 0)
                        video_duration = response_data.get('videoDuration', '00:00')
                        publish_date = response_data.get('publishDate', '')

                        logging.info(f"YeScribe: Successfully extracted {len(transcript)} chars from '{title}' by {author} (duration: {video_duration})")
                        logging.info(f"YeScribe: Video length: {length}s, published: {publish_date}")

                        return transcript

                    logging.warning("YeScribe: No valid text segments found")
                    return None

        except asyncio.TimeoutError:
            logging.error("YeScribe: Request timed out")
            return None
        except Exception as e:
            logging.error(f"YeScribe extraction failed: {str(e)}")
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
            'kome_ai': self._extract_with_kome_ai,
            'anthiago': self._extract_with_anthiago,
            'yescribe': self._extract_with_yescribe,
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
