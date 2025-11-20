"""Simple test script to verify the application setup."""
import sys
import importlib.util


def check_module(module_name):
    """Check if a module can be imported."""
    spec = importlib.util.find_spec(module_name)
    return spec is not None


def main():
    """Run basic checks on the application."""
    print("Image Blur Queues - Setup Verification")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check required modules
    required_modules = [
        'flask',
        'celery',
        'PIL',  # Pillow
        'redis',
        'kombu',
    ]
    
    print("\nChecking required modules:")
    all_ok = True
    for module in required_modules:
        if check_module(module):
            print(f"✓ {module}")
        else:
            print(f"✗ {module} - NOT FOUND")
            all_ok = False
    
    if all_ok:
        print("\n✓ All required modules are installed!")
        print("\nYou can now:")
        print("1. Start RabbitMQ: docker-compose up -d")
        print("2. Start Celery workers:")
        print("   celery -A celery_app worker -Q premium -n premium_worker@%h --loglevel=info")
        print("   celery -A celery_app worker -Q free -n free_worker@%h --loglevel=info")
        print("3. Start Flask app: python app.py")
    else:
        print("\n✗ Some modules are missing. Install them with:")
        print("   pip install -r requirements.txt")
        return 1
    
    # Try to import application modules
    print("\nChecking application modules:")
    app_modules = ['config', 'celery_app', 'tasks', 'app']
    
    for module in app_modules:
        try:
            __import__(module)
            print(f"✓ {module}.py")
        except Exception as e:
            print(f"✗ {module}.py - ERROR: {e}")
            all_ok = False
    
    if all_ok:
        print("\n✓ Application modules loaded successfully!")
        return 0
    else:
        print("\n✗ Some application modules failed to load.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
