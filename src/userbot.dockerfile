FROM python:3.11-alpine

COPY equirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY core /app

COPY userbot /app

ENV PYTHONPATH=/app

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

ENTRYPOINT  ["python", "main.py"]
