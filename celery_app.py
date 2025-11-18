"""Celery application configuration."""
from celery import Celery
from config import Config


def make_celery():
    """Create and configure Celery application."""
    celery = Celery(
        'image_blur_queues',
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=['tasks']
    )
    
    # Configure task routes and priorities
    celery.conf.update(
        task_routes={
            'tasks.blur_image_premium': {'queue': 'premium'},
            'tasks.blur_image_free': {'queue': 'free'},
        },
        task_default_priority=Config.FREE_QUEUE_PRIORITY,
        broker_transport_options={
            'priority_steps': list(range(11)),  # 0-10 priority levels
        },
        worker_prefetch_multiplier=1,  # One task at a time to ensure priority
        task_acks_late=True,  # Acknowledge tasks after completion
    )
    
    return celery


celery = make_celery()
