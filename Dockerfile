# Backend only. Build from repo root.
FROM python:3.11-slim

WORKDIR /app

# System deps for building some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake NLTK data into the image so analysis works on first request
RUN python -c "import nltk; [nltk.download(p, quiet=True) for p in ['punkt', 'punkt_tab', 'stopwords', 'averaged_perceptron_tagger_eng']]"

COPY backend/ ./backend/
RUN mkdir -p /app/data

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
ENV PORT=8000
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
