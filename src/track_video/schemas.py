from typing import List, Optional, Set

from pydantic import BaseModel, HttpUrl


class VideoRequest(BaseModel):
    url: HttpUrl
    objects: Optional[List[str]] = None


class VideoResponse(BaseModel):
    path: str
    ignore: Optional[Set[str]]
