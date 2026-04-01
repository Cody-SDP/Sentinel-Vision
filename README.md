# 🛡️ Sentinel-Vision: AI-Driven Threat Detection
**A project by Cody Sims**

### Overview
Sentinel-Vision is a real-time object detection system optimized for local "Edge" deployment. It is designed to identify specific threats (weapons) and common objects with sub-10ms latency.

### Technical Performance
- **Hardware:** NVIDIA GeForce RTX 4070 SUPER (12GB VRAM)
- **Architecture:** YOLOv11 (Custom Trained)
- **Inference Speed:** ~3.5ms per frame
- **Accuracy:** 0.857 mAP50 (Mean Average Precision)
- **Dataset:** 3,608 custom-annotated images

### Features
- **Zero-Cloud Privacy:** All processing happens locally via CUDA.
- **Real-Time Analysis:** 170-layer neural network with 25M parameters.
- **Cybersecurity Focus:** Designed for autonomous physical security response.