FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data logs exports && \
    echo "[]" > data/users.json && \
    echo "[]" > data/criteria.json && \
    echo "[]" > data/evaluations.json

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/web_app.py

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "src.web_app:app"]
