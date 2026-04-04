from __future__ import annotations

import os
from dataclasses import dataclass

from ultralytics import YOLO


DEFAULT_MODEL_PATH = "yolov8m.pt"


@dataclass(frozen=True)
class ModelLoadResult:
    model: YOLO | None
    model_path: str
    loaded: bool
    error: str | None = None


def resolve_model_path(explicit_path: str | None = None) -> str:
    return explicit_path or os.environ.get("MODEL_PATH") or DEFAULT_MODEL_PATH


def load_model(weights_path: str | None = None) -> ModelLoadResult:
    model_path = resolve_model_path(weights_path)

    if not os.path.exists(model_path):
        return ModelLoadResult(
            model=None,
            model_path=model_path,
            loaded=False,
            error=f"Model file not found: {model_path}",
        )

    try:
        model = YOLO(model_path)
        return ModelLoadResult(model=model, model_path=model_path, loaded=True)
    except Exception as exc:
        return ModelLoadResult(
            model=None,
            model_path=model_path,
            loaded=False,
            error=f"Failed to load model: {exc}",
        )
