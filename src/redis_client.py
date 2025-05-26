import json
from typing import List, Optional
from uuid import uuid4

import redis

from src.config import settings


def get_redis_client() -> redis.Redis:
    return redis.Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True
    )


def add_annotated_video_to_redis(
    username: str,
    url: str,
    objects: Optional[List[str]] = None,
) -> str:
    c_redis = get_redis_client()

    video_id = uuid4().hex

    c_redis.hset(
        f"video:{video_id}",
        mapping={
            "url": url,
            "objects": json.dumps(objects or []),
        },
    )
    c_redis.sadd(f"user:{username}:videos", video_id)

    return video_id
