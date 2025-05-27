from src.redis_client import get_redis_client

def get_videos_by_user(username: str) -> list[dict]:
    redis_client = get_redis_client()

    video_ids = redis_client.smembers(f"user:{username}:videos")

    pipeline = redis_client.pipeline()
    for video_id in video_ids:
        pipeline.hgetall(f"video:{video_id}")
    raw_video_data = pipeline.execute()

    videos = []
    for video in raw_video_data:
        video_dict = {}
        for key, value in video.items():
            video_dict[key] = value
        videos.append(video_dict)

    return videos


