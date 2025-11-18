.PHONY: help install install-dev rabbitmq-start rabbitmq-stop worker-premium worker-free app test clean

help:
	@echo "Image Blur Queues - Available Commands"
	@echo "======================================="
	@echo "install          - Install production dependencies"
	@echo "install-dev      - Install development dependencies"
	@echo "rabbitmq-start   - Start RabbitMQ using Docker Compose"
	@echo "rabbitmq-stop    - Stop RabbitMQ"
	@echo "worker-premium   - Start premium queue worker"
	@echo "worker-free      - Start free queue worker"
	@echo "app              - Start Flask application"
	@echo "test             - Run tests"
	@echo "clean            - Remove Python cache files"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

rabbitmq-start:
	docker-compose up -d
	@echo "RabbitMQ started. Management UI: http://localhost:15672 (guest/guest)"

rabbitmq-stop:
	docker-compose down

worker-premium:
	celery -A celery_app worker -Q premium -n premium_worker@%h --loglevel=info

worker-free:
	celery -A celery_app worker -Q free -n free_worker@%h --loglevel=info

app:
	python app.py

test:
	python test_setup.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
