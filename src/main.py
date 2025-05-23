import uvicorn
from fastapi import FastAPI

from src.load_video import router as upload_router

app = FastAPI()
app.include_router(upload_router, prefix="/video", tags=["Video"])


@app.get("/")
async def ping():
    return "pong"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
