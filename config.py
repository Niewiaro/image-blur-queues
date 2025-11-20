"""Configuration for Flask and Celery."""
import os


class Config:
    """Base configuration."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # Celery settings
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'amqp://guest:guest@localhost:5672//'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'rpc://'
    
    # Queue priorities (higher number = higher priority)
    PREMIUM_QUEUE_PRIORITY = 10
    FREE_QUEUE_PRIORITY = 1
