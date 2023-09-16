FROM python:3.11-alpine

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY core /app/core

COPY userbot /app/userbot

ENV PYTHONPATH=/app

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app/userbot

ENTRYPOINT  ["python", "main.py"]
