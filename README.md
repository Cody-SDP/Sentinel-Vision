# 🛡️ Sentinel-Vision

**Custom-trained, real-time object detection system with a desktop interface (YOLO + PyTorch)**  
Built by Cody Sims

[![Build](https://img.shields.io/github/actions/workflow/status/Cody-SDP/Sentinel-Vision/main.yml?label=build)](https://github.com/Cody-SDP/Sentinel-Vision/actions)
[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![YOLOv8](https://img.shields.io/badge/model-YOLOv8m-purple)]()
[![PyTorch](https://img.shields.io/badge/framework-PyTorch-red)]()
[![CUDA](https://img.shields.io/badge/training-CUDA-green)]()
[![Real-Time](https://img.shields.io/badge/inference-real--time-brightgreen)]()
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow)](https://bandit.readthedocs.io/)
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![mAP](https://img.shields.io/badge/mAP@50-0.85-blue)]()

---

## 🎯 What This Does

Sentinel-Vision is a **locally deployed AI system** that detects objects in real time using a **custom-trained YOLO model**.

- Processes live webcam or video input
- Detects objects frame-by-frame
- Triggers alerts based on confidence thresholds

### 🚨 Demo Behavior
- Alert is triggered when a **cell phone is detected**
- Confidence threshold set to **>90%**
- Designed to demonstrate real-time monitoring + alert logic

---

## 🎥 Preview
![Live Detection](assets/sentinel-vision-preview.png)

---

## 🧠 Model Training & Evaluation

- Model: **YOLOv8m**
- Framework: PyTorch (Ultralytics)
- Training: **transfer learning on custom dataset**
- Hardware: **CUDA-enabled GPU (local training)**
- Epochs: ~50

### 📊 Performance
- Precision: ~0.87  
- Recall: ~0.78  
- mAP@50: ~0.85  
- mAP@50-95: ~0.60  

### 📈 Training Results
![Training Results](assets/results.png)
Training curves show consistent convergence with decreasing loss and increasing precision/recall, indicating stable model learning.

### 📊 Confusion Matrix (Validation Set)
![Confusion Matrix](assets/confusion_matrix.png)

---

## ⚙️ System Overview

Pipeline:

- ~15 FPS real-time inference
- Bounding boxes + class labels + confidence scores
- Adjustable detection threshold
- Runs fully **on-device (no cloud)**

---

## 💻 Application Features

- Real-time object detection
- Webcam + video file input
- Confidence threshold slider
- FPS + system status display
- Multi-camera selection
- Built-in alert system
- Packaged as **Windows desktop app (.exe)**

---

## 🔐 Security & DevOps

- Local-only processing (no external APIs)
- CI/CD pipeline (GitHub Actions)
- **SAST (Bandit)** + dependency scanning (SCA)
- Pinned dependencies for reproducibility

---

## 📦 Install

Download from **Releases**:

Steps:
1. Run installer  
2. Launch app  
3. Select input source  
4. Click **Start**  

> SmartScreen → “More info” → “Run anyway”

---

## 🖥️ Requirements

- Windows OS  
- Webcam (for live detection)  

Runs on CPU for inference.  
GPU (CUDA) was used for **model training (not included in this repo)**.

---

## 📄 License

MIT