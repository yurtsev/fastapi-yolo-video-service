from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import cv2
from tqdm import tqdm
from ultralytics import YOLO

from src.track_video.schemas import AnnotateResponse
from src.track_video.utils import (
    filter_result,
    final_objects,
    ignore_objects,
    model_index,
)

MODEL = YOLO("yolov8n.pt")

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "annotated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def annotate_video(
    input_path: str, objects: Optional[List[str]] = None
) -> AnnotateResponse | None:

    file = Path(input_path).expanduser().resolve()
    if not file.is_file():
        raise FileNotFoundError(file)

    filter_objects = model_index(objects)
    ignore = ignore_objects(objects)
    my_objects = final_objects(objects)

    if filter_objects is None:
        suffix = "all"
    else:
        suffix = "-".join(my_objects)

    out_file = OUTPUT_DIR / f"annotated_{suffix}_{file.stem}.mp4"

    cap = cv2.VideoCapture(str(file))
    if not cap.isOpened():
        raise RuntimeError("Cannot open video file")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    pbar = tqdm(total=total_frames, desc="Annotating", unit="frame")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter.fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_file), fourcc, fps, (width, height))

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            result = MODEL(frame, conf=0.25, verbose=False)[0]
            result = filter_result(result, filter_objects)
            writer.write(result.plot())
            pbar.update(1)

    finally:
        cap.release()
        writer.release()
        pbar.close()

    return AnnotateResponse(path=out_file, ignore=ignore, objects=my_objects)
