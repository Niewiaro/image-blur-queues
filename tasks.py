"""Celery tasks for image processing."""
import base64
from io import BytesIO
from PIL import Image, ImageFilter
from celery_app import celery
from config import Config


def blur_image_data(image_data, blur_radius=10):
    """
    Apply blur effect to image data.
    
    Args:
        image_data: Base64 encoded image data or bytes
        blur_radius: Radius of the blur effect (default: 10)
    
    Returns:
        Base64 encoded blurred image
    """
    # Decode base64 if needed
    if isinstance(image_data, str):
        image_bytes = base64.b64decode(image_data)
    else:
        image_bytes = image_data
    
    # Open image
    image = Image.open(BytesIO(image_bytes))
    
    # Apply blur filter
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # Convert back to base64
    buffered = BytesIO()
    blurred_image.save(buffered, format=image.format or 'PNG')
    blurred_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return blurred_base64


@celery.task(name='tasks.blur_image_premium', priority=Config.PREMIUM_QUEUE_PRIORITY)
def blur_image_premium(image_data, blur_radius=10):
    """
    Process image for premium users (high priority).
    
    Args:
        image_data: Base64 encoded image data
        blur_radius: Radius of the blur effect
    
    Returns:
        Base64 encoded blurred image
    """
    return blur_image_data(image_data, blur_radius)


@celery.task(name='tasks.blur_image_free', priority=Config.FREE_QUEUE_PRIORITY)
def blur_image_free(image_data, blur_radius=10):
    """
    Process image for free users (low priority).
    
    Args:
        image_data: Base64 encoded image data
        blur_radius: Radius of the blur effect
    
    Returns:
        Base64 encoded blurred image
    """
    return blur_image_data(image_data, blur_radius)
