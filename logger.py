"""
PROJECT: Sentinel-Vision (Threat Detection Engine)
AUTHOR: Cody Sims
MODULE: logger.py
DESCRIPTION: Professional structured JSON logging for production-grade audit trails.
             Implements 11 metric categories with rotating file handlers.
"""

import logging
import logging.handlers
import json
import uuid
import os
import subprocess  # nosec B404
import shutil
from datetime import datetime, timezone


def _get_git_context():
    """Retrieve current git commit SHA and branch name for audit traceability."""
    context = {"git_commit": "unknown", "branch": "unknown"}
    git_executable = shutil.which("git")
    if not git_executable:
        return context
    try:
        context["git_commit"] = subprocess.check_output(  # nosec B603
            [git_executable, "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        context["branch"] = subprocess.check_output(  # nosec B603
            [git_executable, "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.SubprocessError, OSError, UnicodeError):
        logging.getLogger(__name__).debug(
            "Unable to resolve git context for logger metadata.",
            exc_info=True,
        )
    return context


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects for machine-readable output."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
        }
        if isinstance(record.msg, dict):
            log_entry.update(record.msg)
        else:
            log_entry["message"] = self.formatMessage(record)
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def _build_logger(name, log_file, max_bytes=10 * 1024 * 1024, backup_count=5):
    """
    Build a logger with:
    - A rotating JSON file handler (10 MB max, 5 backups).
    - A human-readable console handler.
    """
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # --- Rotating JSON file handler ---
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join("logs", log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredJsonFormatter())

        # --- Console handler ---
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(
            logging.Formatter("[%(levelname)s] %(message)s")
        )

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# ---------------------------------------------------------------------------
# Public logger instances
# ---------------------------------------------------------------------------
training_logger = _build_logger("training", "training.log")
inference_logger = _build_logger("inference", "inference.log")


# ---------------------------------------------------------------------------
# Helper: generate a unique run identifier
# ---------------------------------------------------------------------------
def new_run_id():
    return str(uuid.uuid4())[:8]


# ===========================================================================
# 1. RUN INFO
# ===========================================================================
def log_run_info(logger, run_id, module_name):
    """Log run_id, timestamp, git commit, and branch."""
    git = _get_git_context()
    logger.info({
        "event": "run_started",
        "run_id": run_id,
        "module": module_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": git["git_commit"],
        "branch": git["branch"],
    })


# ===========================================================================
# 2. HARDWARE / ENVIRONMENT
# ===========================================================================
def log_hardware(logger, run_id, gpu_name, vram, device_status, throttling=False):
    """Log GPU name, VRAM usage, device status, and throttling warnings."""
    logger.info({
        "event": "hardware_snapshot",
        "run_id": run_id,
        "gpu_name": gpu_name,
        "vram": vram,
        "device_status": device_status,
        "throttling": throttling,
    })
    if throttling:
        logger.warning({
            "event": "gpu_throttling_detected",
            "run_id": run_id,
            "gpu_name": gpu_name,
        })


# ===========================================================================
# 3. MODEL INFO
# ===========================================================================
def log_model_info(logger, run_id, architecture, parameters, checkpoint_path, model_version):
    """Log model architecture, parameter count, checkpoint path, and version."""
    logger.info({
        "event": "model_loaded",
        "run_id": run_id,
        "architecture": architecture,
        "parameters": parameters,
        "checkpoint_path": checkpoint_path,
        "model_version": model_version,
    })


# ===========================================================================
# 4. TRAINING METRICS
# ===========================================================================
def log_training_config(logger, run_id, epochs, image_size, dataset_name, run_name):
    """Log training configuration before a run begins."""
    logger.info({
        "event": "training_config",
        "run_id": run_id,
        "epochs": epochs,
        "image_size": image_size,
        "dataset_name": dataset_name,
        "run_name": run_name,
    })


def log_epoch_metrics(logger, run_id, epoch, total_epochs, loss, accuracy, map50, map_val=None):
    """Log per-epoch training metrics."""
    entry = {
        "event": "epoch_progress",
        "run_id": run_id,
        "epoch": epoch,
        "total_epochs": total_epochs,
        "loss": round(loss, 6) if loss is not None else None,
        "accuracy": round(accuracy, 6) if accuracy is not None else None,
        "mAP50": round(map50, 6) if map50 is not None else None,
    }
    if map_val is not None:
        entry["mAP"] = round(map_val, 6)
    logger.info(entry)


def log_training_complete(logger, run_id, total_epochs, final_accuracy, checkpoint_path):
    """Log training completion and saved checkpoint location."""
    logger.info({
        "event": "training_completed",
        "run_id": run_id,
        "total_epochs": total_epochs,
        "final_accuracy": round(final_accuracy, 6) if final_accuracy is not None else None,
        "checkpoint_path": checkpoint_path,
    })


# ===========================================================================
# 5. EVALUATION METRICS
# ===========================================================================
def log_evaluation_metrics(logger, run_id, precision, recall, false_positives, false_negatives):
    """Log post-training evaluation: precision, recall, FP/FN counts."""
    logger.info({
        "event": "evaluation_metrics",
        "run_id": run_id,
        "precision": round(precision, 6) if precision is not None else None,
        "recall": round(recall, 6) if recall is not None else None,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
    })


# ===========================================================================
# 6. INFERENCE METRICS
# ===========================================================================
def log_inference_detection(logger, run_id, detected_class, confidence, frame_number):
    """Log a single detection event: class, confidence, and frame number."""
    logger.info({
        "event": "threat_detected",
        "run_id": run_id,
        "detected_class": detected_class,
        "confidence": round(confidence, 4) if confidence is not None else None,
        "frame_number": frame_number,
    })


# ===========================================================================
# 7. PERFORMANCE METRICS
# ===========================================================================
def log_performance(logger, run_id, latency_ms, fps, avg_fps=None):
    """Log per-frame latency, current FPS, and rolling average FPS."""
    entry = {
        "event": "performance_metrics",
        "run_id": run_id,
        "latency_ms": round(latency_ms, 3) if latency_ms is not None else None,
        "fps": round(fps, 2) if fps is not None else None,
    }
    if avg_fps is not None:
        entry["avg_fps"] = round(avg_fps, 2)
    logger.info(entry)


# ===========================================================================
# 8. SESSION SUMMARY
# ===========================================================================
def log_session_summary(logger, run_id, total_frames, total_detections, session_duration_s):
    """Log end-of-session summary: frames processed, detections, duration."""
    logger.info({
        "event": "session_summary",
        "run_id": run_id,
        "total_frames": total_frames,
        "total_detections": total_detections,
        "session_duration_s": round(session_duration_s, 2) if session_duration_s is not None else None,
    })


# ===========================================================================
# 9. ERRORS
# ===========================================================================
def log_error(logger, run_id, error_type, message, exception=None):
    """Log GPU failures, model load failures, and input/device failures."""
    entry = {
        "event": "error",
        "run_id": run_id,
        "error_type": error_type,
        "message": message,
    }
    if exception is not None:
        logger.error(entry, exc_info=exception)
    else:
        logger.error(entry)


# ===========================================================================
# 10. WARNINGS
# ===========================================================================
def log_warning(logger, run_id, warning_type, message, current_fps=None, threshold=None):
    """Log low FPS alerts and performance-degradation warnings."""
    entry = {
        "event": "warning",
        "run_id": run_id,
        "warning_type": warning_type,
        "message": message,
    }
    if current_fps is not None:
        entry["current_fps"] = round(current_fps, 2)
    if threshold is not None:
        entry["fps_threshold"] = threshold
    logger.warning(entry)


# ===========================================================================
# 11. OUTPUT TRACKING
# ===========================================================================
def log_output_paths(logger, run_id, output_file_path=None, saved_results_location=None, log_file_location=None):
    """Log output file path, saved results location, and log file location."""
    entry = {
        "event": "output_tracking",
        "run_id": run_id,
    }
    if output_file_path is not None:
        entry["output_file_path"] = output_file_path
    if saved_results_location is not None:
        entry["saved_results_location"] = saved_results_location
    if log_file_location is not None:
        entry["log_file_location"] = log_file_location
    logger.info(entry)
