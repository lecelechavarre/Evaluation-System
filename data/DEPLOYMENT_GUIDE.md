# Complete Deployment Guide

## Quick Start (5 Minutes)

### 1. Extract Package
```bash
unzip performance_eval_system_*.zip
cd performance-eval
```

### 2. Setup Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Initialize System
```bash
python scripts/init_admin.py
# Use defaults: admin / Admin@123
```

### 4. Run Application
```bash
# Web app
python src/web_app.py

# Desktop app
python src/desktop_app.py
```

## Docker Deployment
```bash
docker-compose up -d
```

## Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8000 src.web_app:app
```

See complete documentation in README.md
