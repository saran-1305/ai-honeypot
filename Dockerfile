# Use a slim Python base
FROM python:3.11-slim

# System basics
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Install deps first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . .

# Environment (you can override at docker run)
ENV PORT=8088 \
    OLLAMA_HOST=http://host.docker.internal:11434 \
    HONEYPOT_WEBHOOK=""

EXPOSE 8088

# Start with gunicorn (2 workers, tweak as needed)
CMD ["gunicorn","-w","2","-b","0.0.0.0:8088","app:app"]
