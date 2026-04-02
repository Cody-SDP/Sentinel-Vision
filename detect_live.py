"""
PROJECT: Sentinel-Vision (Threat Detection Engine)
AUTHOR: Cody Sims
DATE: April 1, 2026
ENVIRONMENT: Python 3.12 | CPU or CUDA
DESCRIPTION: Real-time object detection and inference for security applications.
             Supports video file input and webcam input.
"""

import argparse
import os
import sys
import time

from ultralytics import YOLO

import logger as log

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_WEIGHTS_LOCAL = os.path.join("weights", "best.pt")
DEFAULT_WEIGHTS_FALLBACK = "yolov8m.pt"
DEFAULT_SOURCE = os.path.join("demo", "sample.mp4")
DEFAULT_OUTPUT_PATH = os.path.join("runs", "detect", "output")
LOW_FPS_THRESHOLD = 15.0


def _resolve_model_path(cli_path):
    """
    Resolve model weights in priority order:
      1. --model-path CLI argument
      2. MODEL_PATH environment variable
      3. weights/best.pt (custom weights, if the file exists)
      4. yolov8m.pt (Ultralytics auto-download, COCO classes)
    """
    candidates = [p for p in [cli_path, os.environ.get("MODEL_PATH")] if p]
    candidates.append(DEFAULT_WEIGHTS_LOCAL)

    for path in candidates:
        if os.path.exists(path):
            return path

    print(
        f"[INFO] No custom weights found. Falling back to '{DEFAULT_WEIGHTS_FALLBACK}'.\n"
        "       This uses COCO classes (person, car, etc.), NOT custom threat classes.\n"
        f"       To use custom weights, place them at '{DEFAULT_WEIGHTS_LOCAL}' or\n"
        "       pass --model-path /path/to/best.pt"
    )
    return DEFAULT_WEIGHTS_FALLBACK


def _resolve_source(cli_source):
    """
    Resolve the input source:
    - '0' or a numeric digit string → integer webcam index
    - Path to a video file → verified to exist, or a clear error is printed
    - Defaults to DEFAULT_SOURCE with a helpful message if not found
    """
    source = cli_source or os.environ.get("VIDEO_SOURCE") or DEFAULT_SOURCE

    if source.isdigit():
        return int(source)

    if not os.path.exists(source):
        if source == DEFAULT_SOURCE:
            print(
                f"\n[ERROR] Demo video not found: '{DEFAULT_SOURCE}'\n"
                "        To fix this, add any short video file:\n"
                f"            cp /path/to/your/video.mp4 {DEFAULT_SOURCE}\n\n"
                "        Or point to an existing file:\n"
                "            python detect_live.py --source /path/to/video.mp4\n\n"
                "        Or use your webcam:\n"
                "            python detect_live.py --source 0\n",
                file=sys.stderr,
            )
        else:
            print(
                f"\n[ERROR] Source file not found: '{source}'\n"
                "        Check the path and try again.\n",
                file=sys.stderr,
            )
        sys.exit(1)

    return source


def _can_show_gui():
    """Return True only when a graphical display is likely available."""
    if sys.platform == "win32":
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sentinel-Vision — Real-time object detection engine.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Demo mode (sample video, no webcam needed):
  python detect_live.py

  # Webcam mode:
  python detect_live.py --source 0

  # Custom video with saved output:
  python detect_live.py --source my_video.mp4 --save-output

  # Custom weights with live preview:
  python detect_live.py --model-path weights/best.pt --show
        """,
    )
    parser.add_argument(
        "--source",
        default=None,
        help=(
            f"Input source: path to a video file, or '0' for webcam. "
            f"Env var: VIDEO_SOURCE. Default: {DEFAULT_SOURCE}"
        ),
    )
    parser.add_argument(
        "--model-path",
        default=None,
        dest="model_path",
        help=(
            f"Path to YOLO weights (.pt file). Env var: MODEL_PATH. "
            f"Falls back to '{DEFAULT_WEIGHTS_FALLBACK}' if not found."
        ),
    )
    parser.add_argument(
        "--save-output",
        action="store_true",
        dest="save_output",
        help="Save annotated video/frames to disk.",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        dest="output_path",
        help=f"Directory for saved output. Env var: OUTPUT_PATH. Default: {DEFAULT_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show a live preview window (requires a graphical display).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    model_path = _resolve_model_path(args.model_path)
    source = _resolve_source(args.source)

    output_path = (
        args.output_path
        or os.environ.get("OUTPUT_PATH")
        or DEFAULT_OUTPUT_PATH
    )

    show_env = os.environ.get("SHOW_PREVIEW", "").lower()
    show = args.show or show_env in ("1", "true", "yes")
    if show and not _can_show_gui():
        print(
            "[WARNING] --show requested but no graphical display detected. "
            "Disabling live preview. Use --save-output to save results to disk."
        )
        show = False

    # ---------------------------------------------------------------------------
    # Run Info
    # ---------------------------------------------------------------------------
    run_id = log.new_run_id()
    log.log_run_info(log.inference_logger, run_id, "detect_live")

    try:
        # Hardware snapshot
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

        # Model loading
        print(f"[INFO] Loading model: {model_path}")
        model = YOLO(model_path)
        log.log_model_info(
            log.inference_logger, run_id,
            architecture="YOLOv8",
            parameters="~25M",
            checkpoint_path=model_path,
            model_version=os.path.basename(model_path),
        )

        print(f"[INFO] Source: {source}")
        if args.save_output:
            os.makedirs(output_path, exist_ok=True)
            print(f"[INFO] Saving output to: {output_path}")
        print("[INFO] Running inference — press Ctrl+C to stop.\n")

        # Inference loop
        frame_number = 0
        total_detections = 0
        fps_samples = []
        session_start = time.time()

        for result in model.predict(
            source=source,
            show=show,
            stream=True,
            save=args.save_output,
            project=output_path if args.save_output else None,
        ):
            frame_number += 1

            latency_ms = result.speed.get("inference", 0.0) if hasattr(result, "speed") else 0.0
            fps = 1000.0 / latency_ms if latency_ms > 0 else 0.0
            fps_samples.append(fps)
            avg_fps = sum(fps_samples) / len(fps_samples)

            log.log_performance(log.inference_logger, run_id, latency_ms, fps, avg_fps)

            if fps > 0 and fps < LOW_FPS_THRESHOLD:
                log.log_warning(
                    log.inference_logger, run_id,
                    warning_type="low_fps",
                    message="FPS below threshold – possible CPU-bound execution or high system load",
                    current_fps=fps,
                    threshold=LOW_FPS_THRESHOLD,
                )

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

        # Session summary
        session_duration = time.time() - session_start
        log.log_session_summary(
            log.inference_logger, run_id,
            total_frames=frame_number,
            total_detections=total_detections,
            session_duration_s=session_duration,
        )
        log.log_output_paths(
            log.inference_logger, run_id,
            output_file_path=str(source),
            saved_results_location=output_path if args.save_output else None,
            log_file_location=os.path.join("logs", "inference.log"),
        )

        print(
            f"\n[INFO] Done. Processed {frame_number} frame(s), "
            f"{total_detections} detection(s) in {session_duration:.1f}s."
        )
        if args.save_output:
            print(f"[INFO] Annotated output saved to: {output_path}")

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    except Exception as exc:
        log.log_error(log.inference_logger, run_id, "inference_failure", str(exc), exception=exc)
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()