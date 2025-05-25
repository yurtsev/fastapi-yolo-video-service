from pathlib import Path
from typing import List, Optional, Set

from pydantic import BaseModel


class AnnotateResponse(BaseModel):
    path: Path
    objects: Optional[List[str]]
    ignore: Optional[Set[str]]
