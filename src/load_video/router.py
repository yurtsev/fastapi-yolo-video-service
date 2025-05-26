from typing import List, Optional

from fastapi import APIRouter, UploadFile, Request, Response, Query

from src.load_video.schemas import VideoRequest, VideoResponse
from src.load_video.service import (
    download_video_pc,
    download_video_url,
    router_annotate_video,
    set_cookie,
)

router = APIRouter()


@router.post("/url", response_model=VideoResponse)
async def download_video_from_url(request: Request, response: Response, data: VideoRequest) -> VideoResponse:
    session_id = set_cookie(request=request, response=response)
    file_path = download_video_url(str(data.url))
    return router_annotate_video(file_path=file_path, data=data.objects, session_id=session_id)


@router.post("/pc", response_model=VideoResponse)
async def download_video_from_pc(
    uploaded_file: UploadFile,
    request: Request,
    response: Response,
    data: Optional[List[str]] = Query(None),
) -> VideoResponse:
    session_id = set_cookie(request=request, response=response)
    file_path = download_video_pc(uploaded_file)
    return router_annotate_video(file_path=file_path, data=data, session_id=session_id)
