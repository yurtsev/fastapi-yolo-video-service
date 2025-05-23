import re
import socket
from pathlib import Path

import yt_dlp
from fastapi import HTTPException, UploadFile
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

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
    existing = []
    for p in DOWNLOAD_DIR.glob("*.mp4"):
        m = re.fullmatch(r"(\d+)\.mp4", p.name)
        if m:
            existing.append(int(m.group(1)))
    next_id = max(existing, default=0) + 1
    return DOWNLOAD_DIR / f"{next_id}.mp4"


def download_video_pc(uploaded_file: UploadFile) -> Path:

    if not uploaded_file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=400, detail="Invalid file type! Only .mp4 is allowed."
        )

    file = uploaded_file.file
    name = rename_file()
    with open(name, "wb") as f:
        f.write(file.read())

    return name.resolve()


def download_video_url(url: str) -> Path:

    name = rename_file()

    length = get_video_length_from_url(url)
    if length > 300 or length <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid video duration! Only under  300seconds (5 minutes)",
        )

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

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except DownloadError as e:
        msg = str(e).strip()

        if "HTTP Error 404" in msg or "404 Client Error" in msg:
            raise HTTPException(status_code=404, detail="Video not found")

        if "HTTP Error 403" in msg or "403 Client Error" in msg:
            raise HTTPException(status_code=403, detail="Access forbidden")

        raise HTTPException(status_code=502, detail="Download failed")

    except socket.gaierror:

        raise HTTPException(status_code=503, detail="Network error")

    except Exception:

        raise HTTPException(status_code=500, detail="Unexpected error")

    if not name.exists():
        raise HTTPException(
            status_code=500,
            detail="Download reported success but output file is missing",
        )

    return name
