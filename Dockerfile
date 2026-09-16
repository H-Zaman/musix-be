FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PORT=10000
ENV TEMP_DIR=/tmp/ytmp3

# Install FFmpeg, nodejs and clean up apt cache
RUN apt-get update && \
    apt-get install -y ffmpeg curl nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src/app

# Copy requirements
COPY requirements.txt ./

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Ensure temp directory exists and is writable
RUN mkdir -p /tmp/ytmp3 && chmod 777 /tmp/ytmp3

# Expose port (can be overridden by Render)
EXPOSE ${PORT}

# Run FastAPI with uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
