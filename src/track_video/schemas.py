from typing import Optional, List
from pydantic import BaseModel, HttpUrl

class VideoRequest(BaseModel):
    url: HttpUrl
    objects: Optional[List[str]] = None
