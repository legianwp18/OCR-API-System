FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ind \
    poppler-utils \
    build-essential \
    python3-dev \
    libmupdf-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    libpng-dev \
    libtiff-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN mkdir -p uploads results

EXPOSE 8080

CMD ["python", "app.py"]