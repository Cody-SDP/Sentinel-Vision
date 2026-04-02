"""
PROJECT: Sentinel-Vision (Threat Detection Engine)
STUDENT: Cody Sims
AUTHOR: Cody Sims
DATE: April 1, 2026
ENVIRONMENT: Python 3.12 | CUDA 12.1 | NVIDIA RTX 4070 SUPER
DESCRIPTION: Real-time object detection and inference for security applications.
"""

from ultralytics import YOLO
import torch
import os
import time

import logger as log

def main():
    run_id = log.new_run_id()

    # --- 1. Run Info ---
    log.log_run_info(log.training_logger, run_id, "train")

    try:
        # --- 2. Hardware / Environment ---
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram = f"{round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 1)}GB"
            log.log_hardware(log.training_logger, run_id, gpu_name, vram, "available")
            print(f"Using GPU: {gpu_name}")
        else:
            log.log_error(log.training_logger, run_id, "gpu_not_found",
                          "No CUDA-capable GPU detected.")
            print("GPU not found. Check your drivers!")
            return

        # --- 3. Model Info ---
        model = YOLO('yolov8m.pt')
        log.log_model_info(
            log.training_logger, run_id,
            architecture="YOLOv8 Medium",
            parameters="25M",
            checkpoint_path="yolov8m.pt",
            model_version="yolov8m",
        )

        # --- 4. Training Configuration ---
        # Dataset path is read from the DATASET_PATH environment variable so that
        # the script works on any machine without editing source code.  A relative
        # default is provided so contributors can place the dataset in the standard
        # location (datasets/cctv/data.yaml) and run without any extra configuration.
        dataset_path = os.environ.get(
            "DATASET_PATH",
            os.path.join("datasets", "cctv", "data.yaml"),
        )
        run_name = os.environ.get("RUN_NAME", "sentinel_v1")
        epochs = int(os.environ.get("EPOCHS", "1"))
        log.log_training_config(
            log.training_logger, run_id,
            epochs=epochs,
            image_size=640,
            dataset_name=dataset_path,
            run_name=run_name,
        )

        # --- 5. Start Training ---
        start_time = time.time()
        results = model.train(
            data=dataset_path,
            epochs=epochs,
            imgsz=640,
            device=0,
            name=run_name,
        )
        elapsed = time.time() - start_time

        # --- 6. Per-Epoch Metrics (post-training summary) ---
        try:
            map50 = float(results.results_dict.get("metrics/mAP50(B)", 0))
            precision = float(results.results_dict.get("metrics/precision(B)", 0))
            recall = float(results.results_dict.get("metrics/recall(B)", 0))
            box_loss = float(results.results_dict.get("train/box_loss", 0))
        except Exception:
            map50, precision, recall, box_loss = 0.0, 0.0, 0.0, 0.0

        log.log_epoch_metrics(
            log.training_logger, run_id,
            epoch=epochs, total_epochs=epochs,
            loss=box_loss, accuracy=map50, map50=map50,
        )

        # --- 7. Evaluation Metrics ---
        log.log_evaluation_metrics(
            log.training_logger, run_id,
            precision=precision, recall=recall,
            false_positives=None, false_negatives=None,
        )

        # --- 8. Training Completion ---
        checkpoint_path = os.path.join("runs", "detect", run_name, "weights", "best.pt")
        log.log_training_complete(
            log.training_logger, run_id,
            total_epochs=epochs,
            final_accuracy=map50,
            checkpoint_path=checkpoint_path,
        )

        # --- 9. Output Tracking ---
        results_dir = os.path.join("runs", "detect", run_name)
        log.log_output_paths(
            log.training_logger, run_id,
            output_file_path=checkpoint_path,
            saved_results_location=results_dir,
            log_file_location=os.path.join("logs", "training.log"),
        )

        # --- 10. Session Summary ---
        log.log_session_summary(
            log.training_logger, run_id,
            total_frames=None,
            total_detections=None,
            session_duration_s=elapsed,
        )

    except Exception as exc:
        log.log_error(log.training_logger, run_id, "training_failure",
                      str(exc), exception=exc)
        raise

if __name__ == '__main__':
    main()