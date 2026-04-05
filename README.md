# 🛡️ Sentinel-Vision

**Real-time object detection desktop app (YOLO-powered)**  
Built by Cody Sims

[![Build](https://img.shields.io/github/actions/workflow/status/Cody-SDP/Sentinel-Vision/main.yml?label=build)](https://github.com/Cody-SDP/Sentinel-Vision/actions)
[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow)](https://bandit.readthedocs.io/)
[![License](https://img.shields.io/badge/license-MIT-green)]()

---

## 🎥 Preview

<img width="900" alt="Sentinel Vision Demo" src="https://github.com/user-attachments/assets/c76d87ad-db4a-4444-b5e5-3024066efbea" />

> ⚠️ **Demo note:** In this preview, cell phone detection is used as the alert trigger and only activates above **90% confidence**.

---

## Overview

Sentinel-Vision is a local, real-time object detection application for Windows.

It uses a YOLO model to detect objects from:

* your webcam  
* or a video file  

All processing runs locally — no cloud required.

---

## ✨ Features

* Real-time object detection (YOLO)
* Webcam + video file support
* Confidence threshold control
* FPS display
* Multi-camera selection
* Built-in alert system
* Packaged Windows app (no Python required)

---

## 🔐 Security & Pipeline

* **Local-only processing** — no external data transmission  
* No API calls or cloud dependencies  
* CI pipeline includes:
  - **SAST (Bandit)** for static code analysis  
  - **SCA** for dependency vulnerability scanning  
* Security checks run before execution workflows  
* Dependencies are pinned for reproducibility  

This project was built with a security-first mindset, focusing on safe execution, dependency integrity, and controlled runtime behavior.

---

## 📦 Download & Install

Download the latest Windows installer from **Releases**:

- `Sentinel-Vision-Setup-1.3.0.exe`

Then:

1. Run the installer  
2. Complete setup  
3. Launch Sentinel-Vision from your desktop or Start Menu  

> Windows may show a SmartScreen warning → click **More info → Run anyway**

---

## 🧭 Usage

* Select source:
  * Webcam  
  * Video file  
* Click **Start**  
* Adjust confidence if needed  
* View detections in real time  

---

## 🖥️ Requirements

* Windows machine  
* Webcam (for live mode)  

Runs on CPU by default. GPU is optional.

---

## 📝 Notes

* First launch may take a few seconds  
* Performance depends on your hardware  
* This is a desktop AI application — not a cloud service  

---

## 📁 Project

This repository contains:

* application source code  
* build and packaging configuration  
* Windows installer setup  

---

## 📄 License

MIT
