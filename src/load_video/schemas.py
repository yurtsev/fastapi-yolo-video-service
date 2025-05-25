from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class VideoRequest(BaseModel):
    url: HttpUrl = None
    objects: Optional[List[str]] = None


class VideoResponse(BaseModel):
    minio_url: str
    video_id: str
