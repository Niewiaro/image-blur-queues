# Image Blur Queues

A Flask-based microservice with Celery and RabbitMQ for processing image blur requests with priority queues for free and premium users.

## Features

- **Flask REST API** for image upload and result retrieval
- **Celery** for asynchronous task processing
- **RabbitMQ** as message broker
- **Priority Queues**: Premium users get higher priority than free users
- **Image Blur Processing** using Pillow
- Support for multiple image formats (PNG, JPG, JPEG, GIF, BMP)

## Architecture

The service consists of three main components:

1. **Flask App** (`app.py`): REST API for receiving image blur requests
2. **Celery Workers** (`tasks.py`): Process images asynchronously
3. **RabbitMQ**: Message broker with two priority queues
   - `premium` queue: Priority 10 (high)
   - `free` queue: Priority 1 (low)

## Prerequisites

- Python 3.8+
- RabbitMQ server (or use Docker Compose)
- pip for Python package management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Niewiaro/image-blur-queues.git
cd image-blur-queues
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start RabbitMQ using Docker Compose:
```bash
docker-compose up -d
```

Alternatively, install RabbitMQ manually and ensure it's running on `localhost:5672`.

## Usage

### Starting the Services

1. **Start RabbitMQ** (if using Docker):
```bash
docker-compose up -d
```

2. **Start Celery workers** for both queues:

Premium queue worker:
```bash
celery -A celery_app worker -Q premium -n premium_worker@%h --loglevel=info
```

Free queue worker (in a separate terminal):
```bash
celery -A celery_app worker -Q free -n free_worker@%h --loglevel=info
```

3. **Start the Flask application** (in a separate terminal):
```bash
python app.py
```

The API will be available at `http://localhost:5000`.

### API Endpoints

#### 1. Get API Information
```bash
GET /
```

#### 2. Health Check
```bash
GET /health
```

#### 3. Upload Image for Blurring

**Using JSON** (with base64 encoded image):
```bash
POST /blur
Content-Type: application/json

{
  "image": "base64_encoded_image_data",
  "user_type": "premium",  # or "free"
  "blur_radius": 10        # optional, default: 10
}
```

**Using Form Data** (with file upload):
```bash
POST /blur
Content-Type: multipart/form-data

file: <image_file>
user_type: premium  # or "free"
blur_radius: 10     # optional
```

**Example with curl**:
```bash
# Upload with form data
curl -X POST http://localhost:5000/blur \
  -F "file=@image.jpg" \
  -F "user_type=premium"

# Upload with JSON
curl -X POST http://localhost:5000/blur \
  -H "Content-Type: application/json" \
  -d '{"image":"'$(base64 -w 0 image.jpg)'","user_type":"free","blur_radius":15}'
```

**Response**:
```json
{
  "task_id": "abc-123-def-456",
  "user_type": "premium",
  "status": "processing",
  "message": "Image queued for blurring"
}
```

#### 4. Get Result

```bash
GET /result/<task_id>
```

**Example**:
```bash
curl http://localhost:5000/result/abc-123-def-456
```

**Response** (when completed):
```json
{
  "task_id": "abc-123-def-456",
  "status": "completed",
  "image": "base64_encoded_blurred_image",
  "message": "Image blurred successfully"
}
```

**Response** (when pending):
```json
{
  "task_id": "abc-123-def-456",
  "status": "pending",
  "message": "Task is waiting in queue"
}
```

## Configuration

Edit `config.py` to customize settings:

- `SECRET_KEY`: Flask secret key
- `MAX_CONTENT_LENGTH`: Maximum upload file size (default: 16MB)
- `CELERY_BROKER_URL`: RabbitMQ connection URL
- `PREMIUM_QUEUE_PRIORITY`: Priority level for premium users (default: 10)
- `FREE_QUEUE_PRIORITY`: Priority level for free users (default: 1)

## Priority Queue Behavior

- **Premium users** (priority 10) will have their images processed before free users
- **Free users** (priority 1) will wait if premium tasks are in the queue
- Workers process one task at a time to ensure priority is respected
- This is a proof-of-concept implementation demonstrating queue prioritization

## Testing

You can test the priority queue behavior by:

1. Submitting multiple free user requests
2. Submitting a premium user request while free requests are processing
3. Observing that the premium request is processed before remaining free requests

## RabbitMQ Management UI

Access the RabbitMQ management interface at:
```
http://localhost:15672
Username: guest
Password: guest
```

Here you can monitor queues, messages, and worker connections.

## Project Structure

```
image-blur-queues/
├── app.py              # Flask application
├── celery_app.py       # Celery configuration
├── tasks.py            # Celery tasks for image processing
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── docker-compose.yml  # RabbitMQ setup
└── README.md          # This file
```

## Dependencies

- **Flask**: Web framework for REST API
- **Celery**: Distributed task queue
- **Pillow**: Image processing library
- **redis**: Alternative backend for Celery results
- **kombu**: Messaging library for Celery

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

This is a proof-of-concept repository. Feel free to fork and extend the functionality.

## Notes

- Ensure RabbitMQ is running before starting Celery workers
- Workers must be started for both queues (premium and free)
- Images are processed in-memory using base64 encoding
- For production use, consider adding authentication, rate limiting, and persistent storage