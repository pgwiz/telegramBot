FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc tini \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY src ./src

# Run as non-root for safety.
RUN useradd --create-home --uid 1000 bot && chown -R bot:bot /app
USER bot

ENV PYTHONPATH=/app/src
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "/app/src/bot.py"]
