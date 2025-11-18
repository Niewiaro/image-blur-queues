"""Example script demonstrating how to use the Image Blur Queues API."""
import base64
import time
import requests


# API base URL
API_URL = "http://localhost:5000"


def encode_image_to_base64(image_path):
    """Read an image file and encode it to base64."""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def upload_image_json(image_path, user_type='free', blur_radius=10):
    """Upload an image using JSON API."""
    print(f"\n{'='*50}")
    print(f"Uploading image as {user_type} user (JSON method)")
    print(f"{'='*50}")
    
    # Encode image
    image_data = encode_image_to_base64(image_path)
    
    # Prepare request
    payload = {
        'image': image_data,
        'user_type': user_type,
        'blur_radius': blur_radius
    }
    
    # Send request
    response = requests.post(f"{API_URL}/blur", json=payload)
    
    if response.status_code == 202:
        result = response.json()
        print(f"✓ Task created: {result['task_id']}")
        print(f"  Status: {result['status']}")
        print(f"  User type: {result['user_type']}")
        return result['task_id']
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.json())
        return None


def upload_image_multipart(image_path, user_type='free', blur_radius=10):
    """Upload an image using multipart form data."""
    print(f"\n{'='*50}")
    print(f"Uploading image as {user_type} user (Multipart method)")
    print(f"{'='*50}")
    
    # Prepare request
    with open(image_path, 'rb') as image_file:
        files = {'file': image_file}
        data = {
            'user_type': user_type,
            'blur_radius': blur_radius
        }
        
        # Send request
        response = requests.post(f"{API_URL}/blur", files=files, data=data)
    
    if response.status_code == 202:
        result = response.json()
        print(f"✓ Task created: {result['task_id']}")
        print(f"  Status: {result['status']}")
        print(f"  User type: {result['user_type']}")
        return result['task_id']
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.json())
        return None


def check_result(task_id):
    """Check the status and result of a task."""
    print(f"\n{'='*50}")
    print(f"Checking result for task: {task_id}")
    print(f"{'='*50}")
    
    response = requests.get(f"{API_URL}/result/{task_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        
        if result['status'] == 'completed':
            print(f"✓ Image blurred successfully!")
            print(f"  Image data length: {len(result['image'])} characters")
            return result
        elif result['status'] == 'failed':
            print(f"✗ Task failed: {result.get('error')}")
        else:
            print(f"⧗ Task still {result['status']}")
        
        return result
    else:
        print(f"✗ Error: {response.status_code}")
        return None


def wait_for_result(task_id, max_attempts=20, delay=1):
    """Wait for a task to complete."""
    print(f"\nWaiting for task to complete...")
    
    for i in range(max_attempts):
        result = check_result(task_id)
        
        if result and result['status'] == 'completed':
            return result
        elif result and result['status'] == 'failed':
            return result
        
        time.sleep(delay)
    
    print(f"✗ Task did not complete after {max_attempts} attempts")
    return None


def save_blurred_image(image_data, output_path):
    """Save base64 encoded image to file."""
    image_bytes = base64.b64decode(image_data)
    with open(output_path, 'wb') as f:
        f.write(image_bytes)
    print(f"✓ Saved blurred image to: {output_path}")


def demonstrate_priority():
    """Demonstrate priority queue behavior."""
    print("\n" + "="*50)
    print("PRIORITY QUEUE DEMONSTRATION")
    print("="*50)
    print("\nThis will simulate priority queue behavior:")
    print("1. Submit 3 free user requests")
    print("2. Submit 1 premium user request")
    print("3. Premium request should be processed before remaining free requests")
    print("\nNote: You need to have workers running for this to work.")
    print("="*50)
    
    # You would need actual image files to run this
    # Example:
    # task1 = upload_image_json('image1.jpg', 'free')
    # task2 = upload_image_json('image2.jpg', 'free')
    # task3 = upload_image_json('image3.jpg', 'free')
    # task4 = upload_image_json('image4.jpg', 'premium')
    
    print("\nTo run this demonstration:")
    print("1. Ensure RabbitMQ is running: docker-compose up -d")
    print("2. Start workers:")
    print("   celery -A celery_app worker -Q premium -n premium_worker@%h --loglevel=info")
    print("   celery -A celery_app worker -Q free -n free_worker@%h --loglevel=info")
    print("3. Start Flask app: python app.py")
    print("4. Place some test images in the current directory")
    print("5. Uncomment and modify the code above with your image paths")


def main():
    """Main function to demonstrate API usage."""
    print("Image Blur Queues - API Example")
    
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✓ API is running!")
        else:
            print("✗ API returned unexpected status")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure it's running at", API_URL)
        print("\nStart the API with: python app.py")
        return
    
    # Example usage (requires actual image files)
    print("\n" + "="*50)
    print("API USAGE EXAMPLES")
    print("="*50)
    
    print("\n1. Upload with JSON (base64 encoded image):")
    print("   task_id = upload_image_json('image.jpg', 'premium', blur_radius=15)")
    
    print("\n2. Upload with multipart form data:")
    print("   task_id = upload_image_multipart('image.jpg', 'free', blur_radius=10)")
    
    print("\n3. Check result:")
    print("   result = check_result(task_id)")
    
    print("\n4. Wait for result and save:")
    print("   result = wait_for_result(task_id)")
    print("   if result and result['status'] == 'completed':")
    print("       save_blurred_image(result['image'], 'blurred_output.jpg')")
    
    # Demonstrate priority behavior
    demonstrate_priority()


if __name__ == '__main__':
    main()
