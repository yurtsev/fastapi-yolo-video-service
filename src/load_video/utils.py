from pathlib import Path
from uuid import uuid4

from yt_dlp import YoutubeDL

DOWNLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "download"
DOWNLOAD_DIR.mkdir(exist_ok=True)


def get_video_length_from_url(url: str) -> float:

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return float(info.get("duration") or 0.0)


def rename_file() -> Path:
    unique = uuid4().hex[:8]
    return DOWNLOAD_DIR / f"{unique}.mp4"
