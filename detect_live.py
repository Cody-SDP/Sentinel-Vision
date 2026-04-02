"""
PROJECT: Sentinel-Vision (Threat Detection Engine)
STUDENT: Cody Sims
AUTHOR: Cody Sims
DATE: April 1, 2026
ENVIRONMENT: Python 3.12 | CUDA 12.1 | NVIDIA RTX 4070 SUPER
DESCRIPTION: Real-time object detection and inference for security applications.
"""

from ultralytics import YOLO
import time
import os

import logger as log

MODEL_PATH = 'C:/DEV/Sentinel-Vision/runs/detect/sentinel_v12/weights/best.pt'
LOW_FPS_THRESHOLD = 15.0

# --- Run Info ---
run_id = log.new_run_id()
log.log_run_info(log.inference_logger, run_id, "detect_live")

try:
    # --- Hardware / Environment Snapshot ---
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram = f"{round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 1)}GB"
            log.log_hardware(log.inference_logger, run_id, gpu_name, vram, "available")
        else:
            log.log_hardware(log.inference_logger, run_id, "none", "n/a", "cpu_only")
    except Exception as hw_exc:
        log.log_warning(log.inference_logger, run_id, "hardware_check_failed", str(hw_exc))

    # --- Model Info ---
    model = YOLO(MODEL_PATH)
    log.log_model_info(
        log.inference_logger, run_id,
        architecture="YOLOv8 Medium",
        parameters="25M",
        checkpoint_path=MODEL_PATH,
        model_version="yolov8m-custom",
    )

    # --- Inference Loop ---
    frame_number = 0
    total_detections = 0
    fps_samples = []
    session_start = time.time()

    for result in model.predict(source='0', show=True, stream=True):
        frame_start = time.time()
        frame_number += 1

        # Per-frame inference metrics
        latency_ms = result.speed.get("inference", 0.0) if hasattr(result, "speed") else 0.0
        fps = 1000.0 / latency_ms if latency_ms > 0 else 0.0
        fps_samples.append(fps)
        avg_fps = sum(fps_samples) / len(fps_samples)

        log.log_performance(log.inference_logger, run_id, latency_ms, fps, avg_fps)

        # Low FPS warning
        if fps > 0 and fps < LOW_FPS_THRESHOLD:
            log.log_warning(
                log.inference_logger, run_id,
                warning_type="low_fps",
                message="FPS below threshold – possible GPU throttling or high system load",
                current_fps=fps,
                threshold=LOW_FPS_THRESHOLD,
            )

        # Detection event logging
        if result.boxes is not None:
            for box in result.boxes:
                confidence = float(box.conf[0]) if box.conf is not None else 0.0
                class_id = int(box.cls[0]) if box.cls is not None else -1
                class_name = result.names.get(class_id, str(class_id))
                total_detections += 1
                log.log_inference_detection(
                    log.inference_logger, run_id,
                    detected_class=class_name,
                    confidence=confidence,
                    frame_number=frame_number,
                )

    # --- Session Summary ---
    session_duration = time.time() - session_start
    log.log_session_summary(
        log.inference_logger, run_id,
        total_frames=frame_number,
        total_detections=total_detections,
        session_duration_s=session_duration,
    )

    # --- Output Tracking ---
    log.log_output_paths(
        log.inference_logger, run_id,
        output_file_path=MODEL_PATH,
        saved_results_location=os.path.join("runs", "detect"),
        log_file_location=os.path.join("logs", "inference.log"),
    )

except Exception as exc:
    log.log_error(log.inference_logger, run_id, "inference_failure", str(exc), exception=exc)
    raise