from fastapi import APIRouter, Form
from src.load_video.from_url.service import youtube_video

router = APIRouter()

@router.post("/youtube")
def youtube_download(url: str = Form(...)):
    video_path = youtube_video(url)
    return {"video_path": video_path}
