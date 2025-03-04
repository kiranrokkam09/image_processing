# Image Processing System

## Overview
This project is an **Image Processing System** that accepts a CSV file containing product names and image URLs. It processes images asynchronously by downloading and compressing them, storing metadata in a database, and notifying external systems via webhooks.

## Features
- CSV upload API with validation
- Asynchronous image processing using Celery
- Image compression (50% reduction)
- Webhook notifications upon completion
- Database storage using SQLite
- Status tracking via API

## Tech Stack
- **Backend**: Django, Django Rest Framework
- **Database**: SQLite
- **Task Queue**: Celery + Redis
- **Storage**: Local file system
- **Environment**: Running Celery and Redis on WSL

## Installation
### Prerequisites
- Python 3.9+
- Redis (running on WSL)

### Setup
```bash
# Clone the repository
git clone https://github.com/your-repo/image-processing.git
cd image-processing

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

## Running Redis & Celery on WSL
### Start Redis on WSL
```bash
# Open WSL terminal
redis-server
```

### Start Celery Worker
```bash
celery -A image_processing worker --loglevel=info
```

## API Endpoints
### Upload CSV File
**Endpoint:** `POST /upload`
- **Request:** CSV file, optional webhook URL (`webhook_url`)
- **Response:** `{ "request_id": "unique_id" }`

### Check Processing Status
**Endpoint:** `GET /status/{request_id}`
- **Response:** `{ "status": "Pending / Processing / Completed / Failed" }`

### Webhook Callback
- **Triggered on processing completion**
- **Payload:** `{ "request_id": "unique_id", "status": "Completed", "processed_csv": [...] }`

## Postman Collection
[Public Postman Collection Link](https://bit.ly/Postman_Collection)


