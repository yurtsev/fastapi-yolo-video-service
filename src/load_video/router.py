from typing import List, Optional

from fastapi import APIRouter, UploadFile

from src.load_video.service import download_video_pc, download_video_url
from src.track_video import VideoRequest, VideoResponse, annotate_video

router = APIRouter()


@router.post("/url", response_model=VideoResponse)
async def download_video_from_url(data: VideoRequest) -> VideoResponse:
    video_path = download_video_url(str(data.url))
    return annotate_video(str(video_path), data.objects)


@router.post("/pc", response_model=VideoResponse)
async def download_video_from_pc(
    uploaded_file: UploadFile, data: Optional[List[str]] = None
) -> VideoResponse:
    return annotate_video(str(download_video_pc(uploaded_file)), data)
