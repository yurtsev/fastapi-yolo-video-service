from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
from tqdm import tqdm
from ultralytics import YOLO

from src.track_video import VideoResponse

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "annotated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


MODEL = YOLO("yolov8n.pt")


def clean_objects_arr(objects: list[str]) -> list[str]:
    clean_arr = []
    for o in objects:
        cleaned = o.strip().lower()
        clean_arr.append(cleaned)
    return clean_arr


def reverse_dict_model() -> dict[str, int]:
    class_index = {}
    for index, class_name in MODEL.names.items():
        class_index[class_name] = index
    return class_index


def model_index(objects: Optional[list[str]]) -> list[int] | None:
    if not objects:
        return None

    clean_arr = clean_objects_arr(objects)
    class_index = reverse_dict_model()
    result_for_model = []
    for o in clean_arr:
        if o in class_index:
            result_for_model.append(class_index[o])
    return result_for_model or None


def ignore_objects(objects: list[str]) -> set[str] | None:
    clean_arr = clean_objects_arr(objects)
    class_index = reverse_dict_model()
    ignore = set()
    for o in clean_arr:
        if o not in class_index:
            ignore.add(o)
    if ignore:
        return ignore
    return None


def final_objects(objects: list[str]) -> set[str] | None:
    request = clean_objects_arr(objects)
    class_index = reverse_dict_model()
    ignore = set()
    for o in request:
        if o not in class_index:
            ignore.add(o)
    new_objects = set(request) - ignore
    return new_objects


def filter_result(result, target_id: list[int] | None):
    if target_id is None:
        return result

    cls_arr = result.boxes.cls.cpu()
    mask = np.isin(cls_arr, target_id)
    result.boxes = result.boxes[mask]
    return result


def annotate_video(
    input_path: str, objects: Optional[List[str]] = None
) -> VideoResponse | None:

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

    return VideoResponse(path=str(out_file), ignore=ignore)
