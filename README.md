# 🛡️ Sentinel-Vision: AI-Driven Threat Detection
**A project by Cody Sims**

[![Status: Deployment-Ready Foundation](https://img.shields.io/badge/status-deployment--ready%20foundation-brightgreen)](https://github.com/Cody-SDP/Sentinel-Vision)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://bandit.readthedocs.io/)

---

## Overview
Sentinel-Vision is a real-time object detection system optimized for local "Edge" deployment. It is designed to identify specific threats (weapons) and common objects with sub-10ms latency.

---

## 📊 Technical Performance
| Metric | Value |
|--------|-------|
| **Architecture** | YOLOv8 Medium (`yolov8m`) |
| **Inference Speed** | ~3.5 ms per frame |
| **Accuracy** | 0.857 mAP50 |
| **Dataset** | 3,608 custom-annotated images |
| **Parameters** | 25 million |

> **Note on Hardware:** The NVIDIA GeForce RTX 4070 SUPER (12 GB VRAM) specs listed above reflect the **private production runner** only — not end-user hardware requirements.

---

## ✨ Features
- **Zero-Cloud Privacy:** All processing happens locally via CUDA.
- **Real-Time Analysis:** 170-layer neural network with 25M parameters.
- **Cybersecurity Focus:** Designed for autonomous physical security response.
- **Structured Logging:** Professional JSON audit trail with 11 metric categories.
- **Security Gated CI/CD:** Bandit SAST scan must pass before any GPU execution.

---

## 📁 Project Structure
```
Sentinel-Vision/
├── detect_live.py        # Real-time webcam inference (end-user entry point)
├── train.py              # Model training script (contributor/production use)
├── logger.py             # Structured JSON logging module (11 metric categories)
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container image definition
├── .gitignore            # Excludes weights, logs, and training artifacts
├── .github/
│   └── workflows/
│       └── main.yml      # Security-gated CI/CD pipeline
├── logs/                 # Auto-created at runtime (excluded from git)
│   ├── training.log      # Training session audit trail
│   └── inference.log     # Inference session events
└── runs/                 # YOLO training output (excluded from git)
```

---

## 🚀 Quick Start

### 👤 User Instructions (Run on Your Own Webcam)
No special hardware required — works on any machine with Python 3.12 and a webcam.

```bash
# 1. Clone the repository
git clone https://github.com/Cody-SDP/Sentinel-Vision.git
cd Sentinel-Vision

# 2. Install dependencies
pip install -r requirements.txt

# 3. Update the model path in detect_live.py to point to your local weights file

# 4. Run live inference
python detect_live.py
```

Press **Q** in the display window to stop inference. Logs are written to `logs/inference.log`.

---

## 👨‍💻 Contributor Instructions (Security-Gated CI/CD)
Contributors pushing code trigger a two-stage pipeline defined in `.github/workflows/main.yml`:

**Stage 1 — Security Audit (Bandit SAST)**
```bash
bandit -r . -ll -ii
```
All code is scanned for hardcoded credentials, insecure imports, and `shell=True` risks before any hardware is accessed.

**Stage 2 — Hardware Execution (Self-Hosted Runner)**
The second job runs only if Stage 1 passes. It executes on the **private production runner** — an NVIDIA RTX 4070 SUPER workstation that is **not available to end users**. The authorized hardware tag in the workflow refers exclusively to this private machine.

> ⚠️ The `self-hosted` runner is a private production environment. End users do not need this hardware to run `detect_live.py`.

---

## 📝 Logging System

Sentinel-Vision writes structured JSON logs to the `logs/` directory (auto-created, excluded from git).

### Log Files
| File | Contents |
|------|----------|
| `logs/training.log` | GPU init, model loading, epoch progress, training completion |
| `logs/inference.log` | Detection events, confidence scores, latency metrics, FPS |

### File Rotation
- Maximum size: **10 MB** per file
- Retained backups: **5**
- Encoding: UTF-8

### 📈 Tracked Metrics (11 Categories)

| # | Category | Fields |
|---|----------|--------|
| 1 | 🆔 **Run Info** | `run_id`, `timestamp`, `git_commit`, `branch` |
| 2 | 🖥️ **Hardware / Environment** | `gpu_name`, `vram`, `device_status`, `throttling` |
| 3 | 🧠 **Model Info** | `architecture`, `parameters`, `checkpoint_path`, `model_version` |
| 4 | 🏋️ **Training Metrics** | `epochs`, `loss`, `accuracy`, `mAP50`, `dataset_name` |
| 5 | 🧪 **Evaluation Metrics** | `precision`, `recall`, `false_positives`, `false_negatives` |
| 6 | 🎯 **Inference Metrics** | `detected_class`, `confidence`, `frame_number` |
| 7 | ⚡ **Performance Metrics** | `latency_ms`, `fps`, `avg_fps` |
| 8 | 📊 **Session Summary** | `total_frames`, `total_detections`, `session_duration_s` |
| 9 | ❌ **Errors** | `error_type`, `message` (GPU, model, and input failures) |
| 10 | ⚠️ **Warnings** | `warning_type`, `current_fps`, `fps_threshold` |
| 11 | 📁 **Output Tracking** | `output_file_path`, `saved_results_location`, `log_file_location` |

### Example Log Entries

**Training session (training.log)**
```json
{"timestamp": "2026-04-02T12:34:56Z", "level": "INFO", "event": "run_started", "run_id": "a1b2c3d4", "git_commit": "b1fcbb4", "branch": "main"}
{"timestamp": "2026-04-02T12:34:57Z", "level": "INFO", "event": "hardware_snapshot", "run_id": "a1b2c3d4", "gpu_name": "NVIDIA GeForce RTX 4070 SUPER", "vram": "12.0GB", "device_status": "available"}
{"timestamp": "2026-04-02T12:34:58Z", "level": "INFO", "event": "model_loaded", "run_id": "a1b2c3d4", "architecture": "YOLOv8 Medium", "parameters": "25M", "checkpoint_path": "yolov8m.pt"}
{"timestamp": "2026-04-02T12:45:30Z", "level": "INFO", "event": "epoch_progress", "run_id": "a1b2c3d4", "epoch": 1, "loss": 0.234, "accuracy": 0.857, "mAP50": 0.857}
{"timestamp": "2026-04-02T12:45:31Z", "level": "INFO", "event": "evaluation_metrics", "run_id": "a1b2c3d4", "precision": 0.91, "recall": 0.88, "false_positives": 12, "false_negatives": 7}
{"timestamp": "2026-04-02T13:00:00Z", "level": "INFO", "event": "training_completed", "run_id": "a1b2c3d4", "total_epochs": 1, "final_accuracy": 0.857, "checkpoint_path": "runs/detect/sentinel_v1/weights/best.pt"}
{"timestamp": "2026-04-02T13:00:01Z", "level": "INFO", "event": "output_tracking", "run_id": "a1b2c3d4", "output_file_path": "runs/detect/sentinel_v1/weights/best.pt", "log_file_location": "logs/training.log"}
```

**Inference session (inference.log)**
```json
{"timestamp": "2026-04-02T14:00:00Z", "level": "INFO", "event": "run_started", "run_id": "e5f6g7h8", "git_commit": "b1fcbb4", "branch": "main"}
{"timestamp": "2026-04-02T14:00:01Z", "level": "INFO", "event": "model_loaded", "run_id": "e5f6g7h8", "architecture": "YOLOv8 Medium", "checkpoint_path": "runs/detect/sentinel_v12/weights/best.pt"}
{"timestamp": "2026-04-02T14:00:02Z", "level": "INFO", "event": "threat_detected", "run_id": "e5f6g7h8", "detected_class": "weapon", "confidence": 0.94, "frame_number": 45}
{"timestamp": "2026-04-02T14:00:02Z", "level": "INFO", "event": "performance_metrics", "run_id": "e5f6g7h8", "latency_ms": 3.2, "fps": 28.5, "avg_fps": 27.9}
{"timestamp": "2026-04-02T14:05:00Z", "level": "INFO", "event": "session_summary", "run_id": "e5f6g7h8", "total_frames": 8450, "total_detections": 234, "session_duration_s": 300.0}
{"timestamp": "2026-04-02T14:05:01Z", "level": "INFO", "event": "output_tracking", "run_id": "e5f6g7h8", "saved_results_location": "runs/detect", "log_file_location": "logs/inference.log"}
```

---

## 🐳 Deployment (Docker)

### Build the image
```bash
docker build -t sentinel-vision .
```

### Run in CPU mode
```bash
docker run --rm sentinel-vision python detect_live.py
```

### Run with GPU (requires NVIDIA Container Toolkit)
```bash
docker run --rm --gpus all sentinel-vision python detect_live.py
```

---

## ⚙️ Requirements

```
ultralytics          # YOLOv8 model framework
opencv-python-headless  # Video capture and display
requests             # HTTP utilities
python-json-logger   # Structured JSON log formatting
bandit               # Security auditing (SAST)
```

Install all dependencies:
```bash
pip install -r requirements.txt
```