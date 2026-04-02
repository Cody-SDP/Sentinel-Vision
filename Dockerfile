# Use a lightweight Python image — no CUDA required for CPU-based inference
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system libraries required by OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run demo mode by default: processes demo/sample.mp4 and saves annotated output.
# Override by passing arguments: docker run sentinel-vision python detect_live.py --source 0
CMD ["python", "detect_live.py", "--save-output"]