from fastapi import FastAPI

from src.load_video import router as upload_router

app = FastAPI()
app.include_router(upload_router, prefix="/video", tags=["Video"])


@app.get("/")
async def ping():
    return "pong"
