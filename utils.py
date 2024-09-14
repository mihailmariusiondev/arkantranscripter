import re

YOUTUBE_REGEX = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(?:embed\/)?(?:v\/)?(?:shorts\/)?(?:live\/)?(?:[\w\-]{11})"
)

CHUNK_SIZE = 4000
PAUSE_BETWEEN_CHUNKS = 5

def extract_video_id(youtube_url):
    video_id_match = YOUTUBE_REGEX.search(youtube_url)
    if video_id_match:
        return re.search(r"([\w\-]{11})", youtube_url).group(1)
    return None