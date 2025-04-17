from pytube import YouTube
import tempfile

def youtube_video(url: str) -> str:
    yt = YouTube(url)

    stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        stream.download(filename=temp_file.name)
        return temp_file.name
