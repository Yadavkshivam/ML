"""
Flask backend server for Fingerprint Blood Group Detection
Serves trained ML models and provides /predict endpoint
"""

import os
import sys
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
import tempfile
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Get current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Model paths
MODEL_PATHS = {
    'resnet': os.path.join(BASE_DIR, 'code/Resnet34/model_blood_group_detection_resnet.h5'),
    'vgg16': os.path.join(BASE_DIR, 'code/Vgg16/blood_group_detection.h5'),
}

# Blood group class indices
CLASS_INDICES = {0: 'A+', 1: 'A-', 2: 'AB+', 3: 'AB-', 4: 'B+', 5: 'B-', 6: 'O+', 7: 'O-'}

# Loaded models cache
loaded_models = {}


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_model_safe(model_key):
    """Load model from disk with error handling"""
    if model_key in loaded_models:
        return loaded_models[model_key], None

    model_path = MODEL_PATHS.get(model_key)
    if not model_path or not os.path.exists(model_path):
        return None, f"Model {model_key} not found at {model_path}"

    try:
        logger.info(f"Loading model: {model_key} from {model_path}")
        model = load_model(model_path)
        loaded_models[model_key] = model
        logger.info(f"Successfully loaded {model_key}")
        return model, None
    except Exception as e:
        error_msg = f"Failed to load {model_key}: {str(e)}"
        logger.error(error_msg)
        return None, error_msg


def predict_image(model, image_path):
    """Make prediction on single image"""
    try:
        # Load and preprocess image
        img = image.load_img(image_path, target_size=(256, 256))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        # Predict
        predictions = model.predict(x, verbose=0)
        predicted_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_idx]) * 100
        predicted_class = CLASS_INDICES[predicted_idx]

        # All probabilities
        all_probs = {CLASS_INDICES[i]: float(predictions[0][i]) * 100 for i in range(len(CLASS_INDICES))}

        return {
            'available': True,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'all_probabilities': all_probs
        }
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return {
            'available': False,
            'error': str(e)
        }


@app.route('/health', methods=['GET'])
def health_check():
    """Check which models are available"""
    logger.info("Health check requested")
    status = {}
    for model_key in MODEL_PATHS.keys():
        model, error = load_model_safe(model_key)
        status[model_key] = {
            'available': model is not None,
            'error': error
        }
    return jsonify(status), 200


@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    """
    Predict blood group from fingerprint image
    Expects: multipart/form-data with 'file' field
    Returns: { results: [{model, predicted_class, confidence, all_probabilities}, ...] }
    """

    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204

    # Check file in request
    if 'file' not in request.files:
        logger.warning("No file provided in request")
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.warning("Empty filename")
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        logger.warning(f"Invalid file type: {file.filename}")
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    temp_path = None
    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            file.save(tmp.name)
            temp_path = tmp.name
            logger.info(f"File saved to {temp_path}")

        # Run all models
        results = []
        for model_key in MODEL_PATHS.keys():
            model, error = load_model_safe(model_key)

            if model is None:
                results.append({
                    'model': model_key,
                    'available': False,
                    'error': error
                })
                logger.warning(f"Model {model_key} unavailable")
            else:
                prediction = predict_image(model, temp_path)
                prediction['model'] = model_key
                results.append(prediction)
                logger.info(f"Prediction from {model_key}: {prediction['predicted_class']}")

        return jsonify({'results': results}), 200

    except Exception as e:
        error_msg = f'Prediction failed: {str(e)}'
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


@app.route('/', methods=['GET'])
def index():
    """Basic info endpoint"""
    return jsonify({
        'name': 'Fingerprint Blood Group Detection API',
        'version': '1.0',
        'endpoints': {
            'POST /predict': 'Predict blood group from fingerprint image',
            'GET /health': 'Check model availability'
        },
        'models': list(MODEL_PATHS.keys())
    }), 200


if __name__ == '__main__':
    # Development server
    logger.info("=" * 60)
    logger.info("Starting Blood Group Detection Server")
    logger.info("=" * 60)
    logger.info("API available at http://localhost:8000")
    logger.info("Endpoints:")
    logger.info("  POST /predict - Predict blood group from image")
    logger.info("  GET /health - Check model availability")
    logger.info("=" * 60)

    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
