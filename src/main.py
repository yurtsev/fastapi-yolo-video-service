from fastapi import FastAPI
from src.load_video.from_url.router import router as video_router


app = FastAPI()
app.include_router(video_router, prefix="/video", tags=["Video"])

@app.get("/")
async def ping():
    return "pong"