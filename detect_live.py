"""
PROJECT: Sentinel-Vision (Threat Detection Engine)
STUDENT: Cody Sims
AUTHOR: Cody Sims
DATE: April 1, 2026
ENVIRONMENT: Python 3.12 | CUDA 12.1 | NVIDIA RTX 4070 SUPER
DESCRIPTION: Real-time object detection and inference for security applications.
"""

from ultralytics import YOLO

# Load your custom 'Brain'
model = YOLO('C:/DEV/Sentinel-Vision/runs/detect/sentinel_v12/weights/best.pt')

# Run the webcam (0 is your default camera)
results = model.predict(source='0', show=True)