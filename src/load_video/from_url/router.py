from fastapi import APIRouter, Query
from src.load_video.from_url.service import download_video

router = APIRouter()


@router.post("/url")
def download_video_from_url(url: str = Query(...)):
    video_path = download_video(url)
    return {"video_path": video_path}
