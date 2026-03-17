FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY .env .env

ENV HOST=0.0.0.0
ENV PORT=9003
ENV WORKERS=2

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn main:app --host ${HOST} --port ${PORT} --workers ${WORKERS}"]