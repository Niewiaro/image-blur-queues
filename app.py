"""Flask application for image blur service."""
import base64
import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from config import Config
from tasks import blur_image_premium, blur_image_free


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app


app = create_app()


def allowed_file(filename):
    """Check if file extension is allowed."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page with API information."""
    return jsonify({
        'service': 'Image Blur Queues',
        'version': '1.0.0',
        'endpoints': {
            '/': 'API information',
            '/health': 'Health check',
            '/blur': 'POST - Upload image for blurring',
            '/result/<task_id>': 'GET - Retrieve blurred image result'
        }
    })


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


@app.route('/blur', methods=['POST'])
def blur_image():
    """
    Upload image for blurring.
    
    Expected JSON body:
    {
        "image": "base64_encoded_image_data",
        "user_type": "premium" or "free",
        "blur_radius": 10 (optional, default: 10)
    }
    
    Or multipart form-data with:
    - file: image file
    - user_type: "premium" or "free"
    - blur_radius: integer (optional)
    
    Returns:
        JSON with task_id for tracking the blur operation
    """
    user_type = None
    image_data = None
    blur_radius = 10
    
    # Check if request is JSON
    if request.is_json:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_data = data['image']
        user_type = data.get('user_type', 'free')
        blur_radius = data.get('blur_radius', 10)
    
    # Check if request is multipart form-data
    elif 'file' in request.files:
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Read file and convert to base64
        image_bytes = file.read()
        image_data = base64.b64encode(image_bytes).decode('utf-8')
        
        user_type = request.form.get('user_type', 'free')
        blur_radius = int(request.form.get('blur_radius', 10))
    
    else:
        return jsonify({'error': 'No image provided'}), 400
    
    # Validate user_type
    if user_type not in ['premium', 'free']:
        return jsonify({'error': 'Invalid user_type. Must be "premium" or "free"'}), 400
    
    # Dispatch to appropriate queue based on user type
    if user_type == 'premium':
        task = blur_image_premium.apply_async(args=[image_data, blur_radius])
    else:
        task = blur_image_free.apply_async(args=[image_data, blur_radius])
    
    return jsonify({
        'task_id': task.id,
        'user_type': user_type,
        'status': 'processing',
        'message': 'Image queued for blurring'
    }), 202


@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    """
    Get the result of a blur task.
    
    Args:
        task_id: The ID of the blur task
    
    Returns:
        JSON with task status and blurred image (if completed)
    """
    from celery.result import AsyncResult
    
    task = AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'task_id': task_id,
            'status': 'pending',
            'message': 'Task is waiting in queue'
        }
    elif task.state == 'STARTED':
        response = {
            'task_id': task_id,
            'status': 'processing',
            'message': 'Task is being processed'
        }
    elif task.state == 'SUCCESS':
        response = {
            'task_id': task_id,
            'status': 'completed',
            'image': task.result,
            'message': 'Image blurred successfully'
        }
    elif task.state == 'FAILURE':
        response = {
            'task_id': task_id,
            'status': 'failed',
            'error': str(task.info),
            'message': 'Task failed'
        }
    else:
        response = {
            'task_id': task_id,
            'status': task.state.lower(),
            'message': f'Task is in {task.state} state'
        }
    
    return jsonify(response)


if __name__ == '__main__':
    # Debug mode should be disabled in production
    # Set via environment variable: FLASK_DEBUG=False
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
