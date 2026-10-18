# The site was built in 2020 against Python 3.8 and these pinned libraries;
# keep both so it renders exactly as it did then.
FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app app
COPY data data
COPY functions_and_classes functions_and_classes
COPY main.py config.py ./

# Cloud Run sets PORT; the data is loaded once per worker at import time.
CMD exec gunicorn --bind :${PORT:-8080} --workers 2 --threads 4 --timeout 60 main:app
