# 🛡️ Sentinel-Vision: AI-Driven Threat Detection

**A project by Cody Sims**

[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://bandit.readthedocs.io/)

---

## Overview

Sentinel-Vision is a real-time object detection system designed for local "Edge" deployment. It uses a YOLOv8 model to identify objects in video files or live webcam feeds, with structured JSON logging for every inference session.

**Works on CPU — no GPU required.** A GPU will be used automatically if one is available.

> **No bundled sample video.** This repository does not include a video file. You supply your own — either a local video file or your webcam. See [Quick Start](#-quick-start-local) below.

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
- **Flexible Input:** Local video file or webcam via a single flag.
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

# 2. (Recommended) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### A. Test with a local video file

```bash
python detect_live.py --source /path/to/your/video.mp4
```

Add `--save-output` to write annotated frames to `runs/detect/output/predict/`:

```bash
python detect_live.py --source /path/to/your/video.mp4 --save-output
```

### B. Test with your webcam

```bash
python detect_live.py --source 0
# Use --source 1, 2, etc. for additional cameras
```

If no `--source` is provided, the app prints usage instructions and exits cleanly.

Detection results are logged to `logs/inference.log`.

---

## 🐳 Docker Quick Start

### Build

```bash
docker build -t sentinel-vision .
```

### C. Docker — test with a local video file

Mount a directory containing your video file and a `runs/` directory to capture output.

> **First-run prerequisite:** Create the `runs/` directory on your host **before** running the
> container. If it does not exist, Docker creates it as `root:root`, which prevents the
> container's non-root user (`appuser`, UID 1000) from writing output files — causing a
> `PermissionError` at runtime.

```bash
# Step 1 — create the output directory on your host (required once)
mkdir -p runs

# Step 2 — run inference with a mounted video file
docker run --rm \
  -v "/path/to/your/videos:/app/videos" \
  -v "$(pwd)/runs:/app/runs" \
  sentinel-vision \
  python detect_live.py --source /app/videos/clip.mp4 --save-output
```

Annotated frames are saved inside `runs/detect/output/predict/` on your host machine.
YOLO appends a `predict/` sub-directory automatically (incrementing to `predict2/`, `predict3/`, etc. on repeat runs).

### D. Docker — webcam mode (Linux only)

Docker can pass a webcam device through to the container **on Linux only**. macOS and Windows (Docker Desktop) do not support host device passthrough for webcam devices.

On Linux, pass the device node and add the container user to the `video` group. The same `mkdir -p runs` prerequisite applies:

```bash
# Step 1 — create the output directory on your host (required once)
mkdir -p runs

# Step 2 — run inference with a webcam device passed through
docker run --rm \
  --device /dev/video0:/dev/video0 \
  --group-add video \
  -v "$(pwd)/runs:/app/runs" \
  sentinel-vision \
  python detect_live.py --source 0 --save-output
```

> **macOS / Windows:** Docker cannot pass webcam devices through to the container on these platforms. Use local mode (`python detect_live.py --source 0`) instead.

> **Live preview (`--show`) inside Docker** requires X11 forwarding or a display server configured on the host. For most use cases, omit `--show` and use `--save-output` to capture results to disk.

> **Device node:** Webcam device paths vary by system (`/dev/video0`, `/dev/video2`, etc.). Run `ls /dev/video*` on your host to find the correct path before running the container.

---

## 🎬 Input Modes

### Local video file

```bash
python detect_live.py --source /path/to/video.mp4
```

### Webcam mode

```bash
python detect_live.py --source 0
# Use --source 1, 2, etc. for additional cameras
```

### Live preview window

```bash
python detect_live.py --source 0 --show
# Requires a graphical display (not available inside Docker by default)
```

### Save annotated output

```bash
python detect_live.py --source /path/to/video.mp4 --save-output
# Output saved to runs/detect/output/predict/ by default (YOLO appends predict/ automatically)

python detect_live.py --source 0 --save-output --output-path my_results/
```

---

## 🧠 Model Weights

| Situation | What happens |
|-----------|-------------|
| `weights/best.pt` exists | Custom weights are loaded automatically |
| `--model-path /path/to/weights.pt` | Specified weights are loaded |
| Neither is present | Falls back to `yolov8m.pt` (auto-downloaded from Ultralytics, ~52 MB) |

**Fallback note:** `yolov8m.pt` detects COCO classes (person, car, dog, etc.), not the custom threat classes this system was trained for. It is provided as a zero-setup fallback only.

To use custom weights:

```bash
# Place custom weights in the weights/ directory
mkdir weights
cp /path/to/best.pt weights/best.pt

# Or pass the path explicitly
python detect_live.py --source 0 --model-path /path/to/best.pt
```

---

## ⚙️ Configuration

All settings can be controlled via CLI flags or environment variables. Copy `.env.example` to `.env` and set values there, or export them in your shell.

| Flag | Env Var | Default | Description |
|------|---------|---------|-------------|
| `--source` | `VIDEO_SOURCE` | *(none — required)* | Video file path or `0` for webcam |
| `--model-path` | `MODEL_PATH` | `weights/best.pt` → `yolov8m.pt` | Weights file |
| `--output-path` | `OUTPUT_PATH` | `runs/detect/output` | Output directory |
| `--save-output` | — | off | Save annotated video to disk |
| `--show` | `SHOW_PREVIEW=1` | off | Show live preview window |

---

## 🔧 Command Reference

```
python detect_live.py [OPTIONS]

Options:
  --source PATH       Video file path or '0' for webcam (required)
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
- The GPU training job runs only on the upstream repository; forks skip it automatically, so contributors see a clean pass rather than a permanently-queued job.

### Dependency security
All runtime dependencies are pinned to exact versions (`requirements.txt`). Run `bandit -r . -ll -ii` locally or install `pip-audit` to re-verify:

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

---

## 👨‍💻 Contributor Instructions

### Security-Gated CI/CD

Every push triggers a two-stage pipeline:

1. **Bandit SAST** — scans for hardcoded credentials, insecure imports, `shell=True` risks (runs on GitHub-hosted runner for all contributors)
2. **Hardware Execution** — runs only on the private RTX 4070 SUPER runner, and only on the upstream repository (skipped automatically for forks)

Install dev tools locally:

```bash
pip install -r requirements-dev.txt
bandit -r . -ll -ii
```

> ⚠️ The `self-hosted` runner is a private production environment. End users do not need this hardware to run `detect_live.py`.

---

## 🔍 Troubleshooting

**`[ERROR] Permission denied: 'runs/...'` inside Docker**
→ The `runs/` directory was created by Docker as `root`. Remove it and recreate it as your own user before mounting:
```bash
sudo rm -rf runs && mkdir -p runs
```
Then re-run the `docker run` command.

**No source specified (default behavior)**
→ The app prints usage instructions and exits. Pass `--source /path/to/video.mp4` or `--source 0` for webcam.

**`[ERROR] Source file not found: '...'`**
→ Check the path. Use an absolute path if the relative path isn't resolving correctly.

**`[INFO] No custom weights found. Falling back to 'yolov8m.pt'`**
→ Normal on first run. The model (~52 MB) downloads automatically. Place custom weights at `weights/best.pt` to use them.

**`[WARNING] --show requested but no graphical display detected`**
→ You are running in a headless environment (Docker, SSH, CI). Use `--save-output` instead to save results to disk.

**Low FPS warnings**
→ Expected on CPU. Inference at 3–10 FPS on CPU is normal. A GPU will dramatically increase speed.

**`libGL.so.1: cannot open shared object file`** (Linux/Docker)
→ Install: `apt-get install libgl1 libglib2.0-0`

**Webcam not detected in Docker**
→ Pass `--device /dev/video0:/dev/video0 --group-add video` to `docker run`. Linux only — not supported on macOS or Windows Docker Desktop.

---

## ⚠️ Known Limitations

- **No bundled sample video.** The repository does not include a video file. You must supply your own (local file or webcam).
- **Docker output directory:** The `runs/` directory must exist on your host before running the container with `--save-output`. If Docker creates it automatically it will be owned by `root`, causing a `PermissionError` inside the container. Run `mkdir -p runs` first.
- **Webcam in Docker** only works on Linux (`--device /dev/video0 --group-add video`). macOS and Windows users should run locally for webcam support. Device nodes vary by system — check with `ls /dev/video*`.
- **Custom weights** are not included in the repository. The fallback `yolov8m.pt` detects COCO classes, not custom threat classes.
- **Live preview** (`--show`) requires a graphical display and is not available inside a standard Docker container without X11 forwarding.
- **Saved output location:** YOLO appends a `predict/` sub-directory to the output path (e.g. `runs/detect/output/predict/`). On repeat runs this increments to `predict2/`, `predict3/`, etc.