from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
from ultralytics import YOLO

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
