from fastapi import APIRouter, Request, Response

from src.config import settings
from src.load_video import set_cookie
from src.minio_client import get_minio_client
from src.get_video.schemas import HistoryResponse
from src.get_video.service import get_videos_by_user

router = APIRouter()


@router.get("/list/")
async def get_list_objects():
    client = get_minio_client()
    names = []
    for obj in client.list_objects(settings.MINIO_BUCKET_NAME):
        names.append(obj.object_name)
    return {"all videos": names}


@router.get("/history/")
async def get_list_user(request: Request, response: Response) -> HistoryResponse:
    session_id = set_cookie(request=request, response=response)
    videos = get_videos_by_user(session_id)
    return HistoryResponse(user_id=session_id, videos=videos)
