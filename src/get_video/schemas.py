from typing import Optional, List

from pydantic import BaseModel


class HistoryResponse(BaseModel):
    user_id: str
    videos: Optional[List[dict]]
