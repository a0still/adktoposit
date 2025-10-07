import os
import sys
print("Python path:", sys.path)
print("Current directory:", os.getcwd())

try:
    from flask import Flask, render_template, request, jsonify
    print("Flask imported successfully")
except ImportError as e:
    print(f"Failed to import Flask: {e}")

import datetime
try:
    from google.cloud import aiplatform
    from vertexai.generative_models import GenerativeModel, ChatSession
    from google.oauth2 import service_account
    print("Google Cloud libraries imported successfully")
except ImportError as e:
    print(f"Failed to import Google Cloud libraries: {e}")

import pandas as pd

from utils.config import load_config, get_vertex_config
from utils.visualization import create_visualization
from utils.errors import AppError, handle_error, VertexAIError, AuthError
from utils.logging_utils import (
    app_logger,
    auth_logger,
    vertex_logger,
    log_api_call,
    log_vertex_operation,
    log_exception
)

app = Flask(__name__)
chat_model = None

def init_app():
    """Initialize the application."""
    try:
        # Load configuration
        config = load_config('config/agent_config.yaml')
        vertex_config = get_vertex_config()
        
        # Set up credentials
        try:
            credentials = service_account.Credentials.from_service_account_file(
                'key.json',
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
        except Exception as e:
            auth_logger.error("Failed to load service account credentials", exc_info=True)
            raise AuthError("Failed to authenticate with service account") from e
        
        # Initialize Vertex AI
        vertex_logger.info(f"Initializing Vertex AI with config: {vertex_config}")
        try:
            aiplatform.init(
                project=vertex_config['project_id'],
                location=vertex_config['location'],
                credentials=credentials
            )
        except Exception as e:
            vertex_logger.error("Failed to initialize Vertex AI", exc_info=True)
            raise VertexAIError.from_exception(e)
            
        return config, vertex_config
    except (AuthError, VertexAIError) as e:
        raise
    except Exception as e:
        app_logger.error(f"Failed to initialize application: {str(e)}", exc_info=True)
        raise

@log_vertex_operation("initialize_chat_model")
def init_chat_model(vertex_config):
    """Initialize the chat model."""
    global chat_model
    try:
        if chat_model is None:
            chat_model = GenerativeModel("gemini-2.0-flash-001")
            vertex_logger.info("Chat model initialized successfully")
        return True
    except Exception as e:
        vertex_logger.error(f"Failed to initialize chat model: {str(e)}", exc_info=True)
        return False

@app.route('/')
def home():
    """Render the main application page."""
    return render_template('index.html')

@app.route('/health')
@log_api_call
def health():
    """Health check endpoint."""
    try:
        # Check if we can load configuration
        config, vertex_config = init_app()
        
        # Basic connectivity check
        return jsonify({
            'status': 'healthy',
            'checks': {
                'config': True,
                'project_id': vertex_config['project_id'],
                'location': vertex_config['location'],
                'timestamp': datetime.datetime.utcnow().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 500

@app.route('/test', methods=['GET'])
@log_api_call
def test():
    """Test endpoint to verify setup."""
    try:
        config, vertex_config = init_app()
        return jsonify({
            'status': 'success',
            'message': 'Application initialized successfully',
            'config': {
                'project_id': vertex_config['project_id'],
                'location': vertex_config['location']
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/chat', methods=['POST'])
@log_api_call
def chat():
    """Handle chat interactions."""
    try:
        app_logger.info("Chat endpoint called")
        _, vertex_config = init_app()
        app_logger.info(f"App initialized with vertex config: {vertex_config}")
        
        if not init_chat_model(vertex_config):
            app_logger.error("Chat model initialization failed")
            raise VertexAIError("Failed to initialize chat model")
        
        app_logger.info("Chat model initialized successfully")
        data = request.json
        app_logger.info(f"Received data: {data}")
        user_input = data.get('message', '')
        
        if not user_input:
            raise AppError("No message provided", status_code=400)
        
        chat = chat_model.start_chat(
            history=[],
            context="You are a helpful assistant that can analyze data and create visualizations.",
            generation_config={
                "temperature": vertex_config['temperature'],
                "top_p": vertex_config['top_p'],
                "top_k": vertex_config['top_k']
            }
        )
        response = chat.send_message(user_input)
        
        return jsonify({
            'status': 'success',
            'response': response.text
        })
    
    except VertexAIError as e:
        return handle_error(e)
    except AppError as e:
        return handle_error(e)
    except Exception as e:
        error = VertexAIError.from_exception(e)
        return handle_error(error)

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle uncaught exceptions."""
    log_exception(e, {'handler': 'global_error_handler'})
    error = AppError("An unexpected error occurred", status_code=500)
    return handle_error(error)

if __name__ == '__main__':
    try:
        import logging
        # Set up basic logging to console
        logging.basicConfig(level=logging.DEBUG)
        
        # Initialize the app before starting
        config, vertex_config = init_app()
        print(f"Starting application with config: {config}")
        print(f"Vertex AI config: {vertex_config}")
        
        # Initialize the chat model
        if init_chat_model(vertex_config):
            print("Chat model initialized successfully")
        else:
            print("Failed to initialize chat model")
        
        # Start the Flask app
        port = 5000  # Use a different port
        print(f"Starting Flask app on port {port}")
        app.run(host='127.0.0.1', port=port, debug=True)
    except Exception as e:
        import traceback
        print(f"Failed to start application: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())