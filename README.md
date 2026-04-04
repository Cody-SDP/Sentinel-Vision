# 🛡️ Sentinel-Vision

**Real-time object detection desktop app (YOLO-powered)**
Built by Cody Sims

## Preview
<img width="900" alt="Sentinel Vision Demo" src="https://github.com/user-attachments/assets/c76d87ad-db4a-4444-b5e5-3024066efbea" />

[![Build](https://img.shields.io/github/actions/workflow/status/Cody-SDP/Sentinel-Vision/main.yml?label=build)](https://github.com/Cody-SDP/Sentinel-Vision/actions)
[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow)](https://bandit.readthedocs.io/)
[![License](https://img.shields.io/badge/license-MIT-green)]()

---

## Overview

Sentinel-Vision is a local, real-time object detection application for Windows.

It uses a YOLO model to detect objects from:

* your webcam
* or a video file

All processing runs locally — no cloud required.

---

## Features

* Real-time object detection (YOLO)
* Webcam + video file support
* Confidence threshold control
* FPS display
* Multi-camera selection
* Packaged Windows app (no Python required)

---

## Security & Pipeline

* **Local-only processing** — no external data transmission
* No API calls or cloud dependencies
* CI pipeline includes **Bandit static analysis (SAST)**
* Security checks run before execution workflows
* Dependencies are pinned for reproducibility

This project was built with a security-first mindset, including controlled execution and validation in CI/CD.

---

## Download & Run

1. Go to **Releases**
2. Download: `Sentinel-Vision-v1.1.0-windows.zip`
3. Extract the ZIP
4. Open the folder
5. Run `Sentinel-Vision.exe`

> Windows may show a SmartScreen warning → click **More info → Run anyway**

---

## Usage

* Select source:

  * Webcam
  * Video file
* Click **Start**
* Adjust confidence if needed
* View detections in real time

---

## Requirements

* Windows machine
* Webcam (for live mode)

Runs on CPU by default. GPU is optional.

---

## Notes

* First launch may take a few seconds
* Performance depends on your hardware
* This is a desktop AI application — not a cloud service

---

## Project

This repository contains:

* source code
* build configuration
* packaged release

---

## License

MIT
