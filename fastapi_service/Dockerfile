FROM python:3.10-slim

WORKDIR /app

# Установка необходимых системных пакетов
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y upgrade && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install \
        tesseract-ocr \
        tesseract-ocr-rus \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями и устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем скрипт ожидания базы и делаем его исполняемым
COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

# Копируем весь проект в контейнер
COPY . .

# Запуск Celery с ожиданием запуска postgres
CMD ["sh", "-c", "./wait-for-it.sh postgres:5432 --timeout=30 --strict -- celery -A celery_worker.celery_app worker --loglevel=info"]





