from fastapi import APIRouter

from src.load_video.from_url import download_video_url
from src.track_video import VideoRequest, VideoResponse
from src.track_video import annotate_video

router = APIRouter()


@router.post("/url", response_model=VideoResponse)
def download_video_from_url(data: VideoRequest) -> VideoResponse:
    video_path = download_video_url(str(data.url))
    return annotate_video(str(video_path), data.objects)
