# Use a professional NVIDIA base image with Python and CUDA pre-installed
FROM nvidia/cuda:12.1.0-base-ubuntu22.04

# Set the working directory inside the container
WORKDIR /app

# Install Python and essential libraries
RUN apt-get update && apt-get install -y python3 python3-pip

# Copy your local code into the container
COPY . .

# Install the AI engine and requirements
RUN pip3 install ultralytics opencv-python-headless requests

# Tell the container to run your detection script by default
CMD ["python3", "detect_live.py"]