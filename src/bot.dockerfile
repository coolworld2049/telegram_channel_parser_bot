FROM python:3.11

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY core /app/core

COPY bot /app/bot

ENV PYTHONPATH=/app

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app/bot

ENTRYPOINT  ["python", "main.py"]
