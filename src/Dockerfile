FROM python:3.11

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY bot /app

ENV PYTHONPATH=/app

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

ENTRYPOINT  ["python", "main.py"]
