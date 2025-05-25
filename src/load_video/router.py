from typing import List, Optional

from fastapi import APIRouter, UploadFile

from src.load_video.schemas import VideoRequest, VideoResponse
from src.load_video.service import (
    download_video_pc,
    download_video_url,
    router_annotate_video,
)

router = APIRouter()


@router.post("/url", response_model=VideoResponse)
async def download_video_from_url(data: VideoRequest) -> VideoResponse:
    video_path = download_video_url(str(data.url))
    return router_annotate_video(video_path, data.objects)


@router.post("/pc", response_model=VideoResponse)
async def download_video_from_pc(
    uploaded_file: UploadFile, data: Optional[List[str]] = None
) -> VideoResponse:
    file_path = download_video_pc(uploaded_file)
    return router_annotate_video(file_path, data)
