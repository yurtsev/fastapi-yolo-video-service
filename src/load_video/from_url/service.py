from pathlib import Path
import yt_dlp
import re

DOWNLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "download"
DOWNLOAD_DIR.mkdir(exist_ok=True)

def rename_file() -> Path:
    existing = []
    for p in DOWNLOAD_DIR.glob("*.mp4"):
        m = re.fullmatch(r"(\d+)\.mp4", p.name)
        if m:
            existing.append(int(m.group(1)))
    next_idx = max(existing, default=0) + 1
    return DOWNLOAD_DIR / f"{next_idx}.mp4"

def download_video_url(url: str) -> Path:
    name = rename_file()

    ydl_opts = {
        "outtmpl": str(name),
        "format": (
            "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]"
            "/best[ext=mp4][vcodec^=avc1]"
            "/best"
        ),
        "merge_output_format": "mp4",
        "ffmpeg_location": "/opt/homebrew/bin/ffmpeg",
        "fixup": "detect_or_warn",
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if not name.exists():
        raise RuntimeError("yt-dlp did not produce an .mp4 file")

    return name
