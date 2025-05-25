import json
from typing import List, Optional, Set
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
    ignore: Optional[Set[str]] = None,
) -> str:
    c_redis = get_redis_client()

    video_id = uuid4().hex

    c_redis.hset(
        f"video:{video_id}",
        mapping={
            "url": url,
            "objects": json.dumps(objects or []),
            "ignore": json.dumps(list(ignore or [])),
        },
    )
    c_redis.sadd(f"user:{username}:videos", video_id)

    return video_id


def get_videos_by_user(username: str) -> list[dict]:
    c_redis = get_redis_client()

    ids = c_redis.smembers(f"user:{username}:videos")
    pipe = c_redis.pipeline()
    for vid in ids:
        pipe.hgetall(f"video:{vid}")
    raw = pipe.execute()
    return [{k: v for k, v in doc.items()} for doc in raw]
