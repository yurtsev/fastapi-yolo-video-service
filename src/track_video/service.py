from __future__ import annotations

from pathlib import Path
from typing import Sequence, Optional

import cv2
import numpy as np
from ultralytics import YOLO


OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "annotated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


MODEL = YOLO("yolov8n.pt")


NAME_TO_IDX = {v: k for k, v in MODEL.names.items()}


def normalize(objects: Optional[list[str]]) -> Optional[list[int]]:
    if not objects:
        return None
    idx = [i for i, n in MODEL.names.items() if n in {o.strip().lower() for o in objects}]
    return idx or None



def filter_result(result, target_idx: list[int] | None):
    if target_idx is None:
        return result

    cls_arr = result.boxes.cls.cpu().numpy()
    mask = np.isin(cls_arr, target_idx)
    result.boxes = result.boxes[mask]
    return result



def annotate_video(input_path: str, objects: str | Sequence[str] | None = None) -> str:

    src = Path(input_path).expanduser().resolve()
    if not src.is_file():
        raise FileNotFoundError(src)

    obj_list = normalize(objects)
    idx_list = None if obj_list is None else [NAME_TO_IDX[o] for o in obj_list]

    suffix = "all" if obj_list is None else "-".join(obj_list)
    dst = OUTPUT_DIR / f"annotated_{suffix}_{src.stem}.mp4"

    cap = cv2.VideoCapture(str(src))
    if not cap.isOpened():
        raise RuntimeError("Cannot open video file")

    width, height = (
        int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    )
    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    fourcc = cv2.VideoWriter.fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(dst), fourcc, fps, (width, height))

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            result = MODEL(frame, conf=0.25, verbose=False)[0]
            result = filter_result(result, idx_list)
            writer.write(result.plot())
    finally:
        cap.release()
        writer.release()

    return str(dst)

