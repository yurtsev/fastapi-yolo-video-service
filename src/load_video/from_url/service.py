from pytube import YouTube
import tempfile
import yt_dlp

def youtube_video(url: str) -> str:
    yt = YouTube(url)

    stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        stream.download(filename=temp_file.name)
        return temp_file.name


def download_video(url: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        ydl_opts = {"outtmpl": temp_file.name, "format": "best[ext=mp4]/best", "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return temp_file.name

