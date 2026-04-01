"""
PROJECT: Sentinel-Vision (Threat Detection Engine)
STUDENT: Cody Sims
AUTHOR: Cody Sims
DATE: April 1, 2026
ENVIRONMENT: Python 3.12 | CUDA 12.1 | NVIDIA RTX 4070 SUPER
DESCRIPTION: Real-time object detection and inference for security applications.
"""

from ultralytics import YOLO
import torch

def main():
    # 1. Verify GPU is ready (NVIDIA instructors love this check)
    if torch.cuda.is_available():
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("GPU not found. Check your drivers!")
        return

    # 2. Load the model (using the 'Medium' version for better school security)
    model = YOLO('yolov8m.pt') 

    # 3. Start Training
    model.train(
        data='C:/DEV/Sentinel-Vision/datasets/cctv/data.yaml',
        epochs=50, 
        imgsz=640, 
        device=0,      # Force it to use your NVIDIA GPU
        name='sentinel_v1' # This names your output folder
    )

if __name__ == '__main__':
    main()