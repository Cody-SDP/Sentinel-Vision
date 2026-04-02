# 🛡️ Sentinel-Vision: AI-Driven Threat Detection

**A project by Cody Sims**

[![Status: Deployment-Ready Foundation](https://img.shields.io/badge/status-deployment--ready%20foundation-brightgreen)](https://github.com/Cody-SDP/Sentinel-Vision)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://bandit.readthedocs.io/)

---

## Overview

Sentinel-Vision is a real-time object detection system designed for local "Edge" deployment. It uses a YOLOv8 model to identify objects in video files or live webcam feeds, with structured JSON logging for every inference session.

**Works on CPU — no GPU required.** A GPU will be used automatically if one is available.

---

## 📊 Technical Performance

| Metric | Value |
|--------|-------|
| **Architecture** | YOLOv8 Medium (`yolov8m`) |
| **Inference Speed** | ~3.5 ms per frame (GPU) |
| **Accuracy** | 0.857 mAP50 (custom dataset) |
| **Dataset** | 3,608 custom-annotated images |
| **Parameters** | 25 million |

> **Note on Hardware:** The NVIDIA GeForce RTX 4070 SUPER specs above reflect the private production runner only — not end-user requirements.

---

## ✨ Features

- **Zero-Cloud Privacy:** All processing happens locally.
- **CPU & GPU:** Runs on any modern machine; CUDA accelerates if available.
- **Plug-and-Play:** Works out of the box with a sample video — no source edits needed.
- **Flexible Input:** Video file or webcam via a single flag.
- **Structured Logging:** JSON audit trail with 11 metric categories written to `logs/inference.log`.
- **Saved Output:** Annotated video/frames can be saved to disk with `--save-output`.

---

## 📁 Project Structure

```
Sentinel-Vision/
├── detect_live.py        # Main entry point — inference on video or webcam
├── train.py              # Model training script (contributor/production use)
├── logger.py             # Structured JSON logging module
├── requirements.txt      # Runtime Python dependencies (pinned)
├── requirements-dev.txt  # Development tools (bandit, etc.)
├── Dockerfile            # CPU-friendly container image
├── .env.example          # Optional environment variable reference
├── demo/
│   ├── README.md         # Instructions for adding a sample video
│   └── sample.mp4        # ← Add your own video here (not tracked by git)
├── weights/
│   └── best.pt           # ← Place custom weights here (not tracked by git)
├── logs/                 # Auto-created at runtime
│   └── inference.log     # Inference session audit trail
└── runs/                 # YOLO output (auto-created, not tracked by git)
```

---

## 🚀 Quick Start (Local)

### Prerequisites

- Python 3.12
- `pip`
- A video file **or** a webcam

```bash
# 1. Clone the repository
git clone https://github.com/Cody-SDP/Sentinel-Vision.git
cd Sentinel-Vision

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add a sample video (any .mp4 clip works)
cp /path/to/your/video.mp4 demo/sample.mp4

# 4. Run demo mode
python detect_live.py
```

That's it. Detection results are logged to `logs/inference.log`.

---

## 🐳 Docker Quick Start

### Build

```bash
docker build -t sentinel-vision .
```

### Demo mode (sample video — no webcam needed)

```bash
# Mount the demo/ folder so the container can read your sample video,
# and mount runs/ so annotated output is saved to your host machine.
docker run --rm \
  -v "$(pwd)/demo:/app/demo" \
  -v "$(pwd)/runs:/app/runs" \
  sentinel-vision
```

Annotated frames are saved to `runs/detect/output/` on your host.

### Webcam mode (Linux only)

```bash
docker run --rm \
  --device /dev/video0:/dev/video0 \
  -v "$(pwd)/runs:/app/runs" \
  sentinel-vision python detect_live.py --source 0 --save-output
```

> **macOS / Windows:** Docker cannot pass webcam devices through to the container on these platforms. Use local mode (`python detect_live.py --source 0`) instead.

---

## 🎬 Input Modes

### Demo mode — sample video

```bash
python detect_live.py
# or explicitly:
python detect_live.py --source demo/sample.mp4
```

### Webcam mode

```bash
python detect_live.py --source 0
# Use --source 1, 2, etc. for additional cameras
```

### Live preview window

```bash
python detect_live.py --show
# Requires a graphical display (not available inside Docker by default)
```

### Save annotated output

```bash
python detect_live.py --save-output
# Output saved to runs/detect/output/ by default

python detect_live.py --save-output --output-path my_results/
```

---

## 🧠 Model Weights

| Situation | What happens |
|-----------|-------------|
| `weights/best.pt` exists | Custom weights are loaded automatically |
| `--model-path /path/to/weights.pt` | Specified weights are loaded |
| Neither is present | Falls back to `yolov8m.pt` (auto-downloaded from Ultralytics, ~52 MB) |

**Fallback note:** `yolov8m.pt` detects COCO classes (person, car, dog, etc.), not the custom threat classes this system was trained for. It is provided as a zero-setup demo only.

To use custom weights:

```bash
# Place custom weights in the weights/ directory
mkdir weights
cp /path/to/best.pt weights/best.pt

# Or pass the path explicitly
python detect_live.py --model-path /path/to/best.pt
```

---

## ⚙️ Configuration

All settings can be controlled via CLI flags or environment variables. Copy `.env.example` to `.env` and set values there, or export them in your shell.

| Flag | Env Var | Default | Description |
|------|---------|---------|-------------|
| `--source` | `VIDEO_SOURCE` | `demo/sample.mp4` | Input file or `0` for webcam |
| `--model-path` | `MODEL_PATH` | `weights/best.pt` → `yolov8m.pt` | Weights file |
| `--output-path` | `OUTPUT_PATH` | `runs/detect/output` | Output directory |
| `--save-output` | — | off | Save annotated video to disk |
| `--show` | `SHOW_PREVIEW=1` | off | Show live preview window |

---

## 🔧 Command Reference

```
python detect_live.py [OPTIONS]

Options:
  --source PATH       Video file path or '0' for webcam
  --model-path PATH   Path to .pt weights file
  --save-output       Save annotated output to disk
  --output-path DIR   Directory for saved output
  --show              Show live preview window
  -h, --help          Show this message and exit
```

---

## 📝 Logging

Structured JSON logs are written to `logs/inference.log` (auto-created). Each run records:

- Run ID, timestamp, git commit, branch
- Hardware info (GPU name, VRAM, or CPU-only status)
- Model info (architecture, weights path)
- Per-frame: latency, FPS, detection class, confidence
- Session summary: total frames, detections, duration

Log files rotate at 10 MB, keeping the last 5 backups.

---

## 🔒 Security

### Container security
The Docker image runs as a non-root user (`appuser`, UID 1000). A `.dockerignore` file prevents `.env` files, `.git/` history, and model weights from being copied into the image at build time.

### Secrets management
- Never commit a populated `.env` file. It is listed in `.gitignore`.
- Use the provided `.env.example` as a reference — copy it to `.env` locally and populate as needed.
- Model paths, dataset paths, and video sources are all controlled via environment variables or CLI flags — no secrets are hardcoded.

### CI/CD security
- The GitHub Actions workflow has a top-level `permissions: contents: read` block, restricting the default `GITHUB_TOKEN` to read-only access.
- `bandit` is pinned to `1.8.3` both in `requirements-dev.txt` and the CI install step, preventing silent scan-behaviour changes from upstream upgrades.
- The Bandit SAST gate must pass before the self-hosted GPU runner is accessed.

### Dependency security
All runtime dependencies are pinned to exact versions (`requirements.txt`). No known CVEs exist against the pinned versions (verified at time of last audit). Run `bandit -r . -ll -ii` locally or install `pip-audit` to re-verify:

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

---

## 👨‍💻 Contributor Instructions

### Security-Gated CI/CD

Every push triggers a two-stage pipeline:

1. **Bandit SAST** — scans for hardcoded credentials, insecure imports, `shell=True` risks
2. **Hardware Execution** — runs only if Stage 1 passes, on the private RTX 4070 SUPER runner

Install dev tools locally:

```bash
pip install -r requirements-dev.txt
bandit -r . -ll -ii
```

> ⚠️ The `self-hosted` runner is a private production environment. End users do not need this hardware to run `detect_live.py`.

---

## 🔍 Troubleshooting

**`[ERROR] Demo video not found: 'demo/sample.mp4'`**
→ Add any `.mp4` file: `cp /path/to/video.mp4 demo/sample.mp4`

**`[INFO] No custom weights found. Falling back to 'yolov8m.pt'`**
→ Normal on first run. The model (~52 MB) downloads automatically. Place custom weights at `weights/best.pt` to use them.

**`[WARNING] --show requested but no graphical display detected`**
→ You are running in a headless environment (Docker, SSH, CI). Use `--save-output` instead to save results to disk.

**Low FPS warnings**
→ Expected on CPU. Inference at 3–10 FPS on CPU is normal. A GPU will dramatically increase speed.

**`libGL.so.1: cannot open shared object file`** (Linux/Docker)
→ Install: `apt-get install libgl1 libglib2.0-0`

**Webcam not detected in Docker**
→ Pass `--device /dev/video0:/dev/video0` to `docker run`. Linux only — not supported on macOS or Windows Docker Desktop.

---

## ⚠️ Known Limitations

- **Webcam in Docker** only works on Linux (`--device /dev/video0`). macOS and Windows users should run locally for webcam support.
- **Custom weights** are not included in the repository. The fallback `yolov8m.pt` detects COCO classes, not custom threat classes.
- **Live preview** (`--show`) requires a graphical display and is not available inside a standard Docker container without X11 forwarding.