import uvicorn
from fastapi import FastAPI

from src.get_video import router as get_video_router
from src.load_video import router as upload_video_router

app = FastAPI()
app.include_router(upload_video_router, prefix="/upload_video", tags=["annotate"])
app.include_router(get_video_router, prefix="/get_video", tags=["get_video"])


@app.get("/")
async def ping():
    return "pong"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
