from fastapi import APIRouter
from src.track_video.schemas import VideoRequest
from src.track_video.service import annotate_video
from src.load_video.from_url.service import download_video_url


router = APIRouter()


@router.post("/url")
def download_video_from_url(data: VideoRequest) -> str:
    video_path = download_video_url(str(data.url))
    return annotate_video(video_path, data.objects)
