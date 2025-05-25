import socket
from pathlib import Path
from typing import List, Optional

import yt_dlp
from fastapi import HTTPException, UploadFile
from yt_dlp.utils import DownloadError

from src.load_video.schemas import VideoResponse
from src.load_video.utils import get_video_length_from_url, rename_file
from src.minio_client import upload_file_to_minio
from src.redis_client import add_annotated_video_to_redis
from src.track_video import annotate_video


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


def router_annotate_video(
    file_path: Path, data: Optional[List[str]] = None
) -> VideoResponse:

    result = annotate_video(str(file_path), data)

    video_path = result.path
    ignore = result.ignore
    objects = result.objects

    link = upload_file_to_minio(video_path)
    video_path.unlink(missing_ok=True)
    file_path.unlink(missing_ok=True)

    video_id = add_annotated_video_to_redis(
        username="yurtsev", url=link, objects=objects, ignore=ignore
    )

    return VideoResponse(minio_url=link, video_id=video_id)
