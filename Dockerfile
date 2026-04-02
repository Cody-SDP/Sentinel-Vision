# Use a lightweight Python image — no CUDA required for CPU-based inference
FROM python:3.12-slim

# Install system libraries required by OpenCV and create a non-root user in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    # Create a dedicated, unprivileged user to run the application.
    # Running as root inside a container widens the blast radius of any
    # exploited vulnerability; a non-root user limits what an attacker can do.
    && useradd -m -u 1000 appuser

# Set the working directory and give the non-root user ownership so it can
# create logs/, runs/, etc. at runtime without requiring root access.
WORKDIR /app
RUN chown appuser:appuser /app

# Install Python dependencies as root so they land in the system-wide site-packages
# (readable by all users).  This must happen before switching to appuser.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code with correct ownership from the start
COPY --chown=appuser:appuser . .

# Drop to the non-root user for all subsequent commands and the container runtime
USER appuser

# Run demo mode by default: processes demo/sample.mp4 and saves annotated output.
# Override by passing arguments: docker run sentinel-vision python detect_live.py --source 0
CMD ["python", "detect_live.py", "--save-output"]