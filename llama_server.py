#!/usr/bin/env python3
"""
AINZUNI Llama 3.1:8b Integration Server - OPTIMIZED FOR SPEED
This server provides an API endpoint for the AINZUNI chatbot to connect with Llama 3.1:8b via Ollama.
"""

import requests
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import logging
from functools import lru_cache

# CONFIGURE LOGGING - Track server operations and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# INITIALIZE FLASK APP - Create web server with CORS support
app = Flask(__name__)
CORS(app)  # Enable cross-origin requests for frontend

# CONFIGURATION - Server settings and model parameters (OPTIMIZED FOR SPEED)
OLLAMA_BASE_URL = "http://localhost:11434"  # Ollama API endpoint
MODEL_NAME = "llama3.1:8b"                  # AI model to use
DEFAULT_TEMPERATURE = 0.5                   # Reduced for faster, more focused responses
DEFAULT_TOP_P = 0.8                         # Optimized for speed
DEFAULT_MAX_TOKENS = 300                    # Reduced for faster responses
REQUEST_TIMEOUT = 120                       # Increased timeout to avoid premature failures on slow machines

# NZ UNIVERSITIES CONTEXT - Knowledge base for better AI responses
NZ_UNIVERSITIES_CONTEXT = """
You are AINZUNI, an AI assistant specializing in New Zealand universities and higher education. 
Keep responses concise and helpful. Focus on key information about:

1. New Zealand's 8 universities:
   - University of Auckland, University of Otago, Victoria University of Wellington
   - University of Canterbury, Massey University, University of Waikato
   - Lincoln University, Auckland University of Technology

2. Academic programs, admission requirements, campus life, international student info.

Provide accurate, helpful, and concise responses.
"""

# CACHE FOR CONNECTION STATUS - Reduces repeated API calls
@lru_cache(maxsize=1)
def get_cached_ollama_status():
    """Cached version of Ollama status check to reduce API calls."""
    return check_ollama_status()

def check_ollama_status():
    """
    Check if Ollama is running and the model is available.
    Returns: True if model is available, False otherwise
    """
    try:
        # Test connection to Ollama API with reduced timeout
        logger.info(f"Checking Ollama status at {OLLAMA_BASE_URL}")
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)  # Reduced timeout
        logger.info(f"Ollama response status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse available models from response
            data = response.json()
            models = data.get("models", [])
            model_names = [model.get("name", "") for model in models]
            logger.info(f"Available models: {model_names}")
            
            # Check if our target model is available
            model_available = MODEL_NAME in model_names
            logger.info(f"Model {MODEL_NAME} available: {model_available}")
            return model_available
        else:
            logger.error(f"Ollama returned status {response.status_code}: {response.text}")
            return False
    except requests.exceptions.Timeout:
        logger.error("Timeout connecting to Ollama")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Connection error - Ollama may not be running")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking Ollama status: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking Ollama: {e}")
        return False

def warmup_model():
    """
    Warm up the model with a simple request to ensure it's loaded.
    This reduces response time for the first user request.
    Returns: True if warmup successful, False otherwise
    """
    try:
        logger.info("Warming up model...")
        warmup_payload = {
            "model": MODEL_NAME,
            "prompt": "Hello",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.8,
                "num_predict": 5  # Reduced for faster warmup
            }
        }
        
        # Send warmup request to Ollama with reduced timeout
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=warmup_payload,
            timeout=30  # Reduced timeout
        )
        
        if response.status_code == 200:
            logger.info("Model warmup successful")
            return True
        else:
            logger.warning(f"Model warmup failed: {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"Model warmup error: {e}")
        return False

def generate_response(prompt, temperature=DEFAULT_TEMPERATURE, top_p=DEFAULT_TOP_P, max_tokens=DEFAULT_MAX_TOKENS, request_timeout=REQUEST_TIMEOUT, _retry=False):
    """
    Generate a response using Llama 3.1:8b via Ollama - OPTIMIZED FOR SPEED.
    
    Args:
        prompt (str): User's question/message
        temperature (float): Controls response randomness (reduced for speed)
        top_p (float): Controls response diversity (optimized)
        max_tokens (int): Maximum response length (reduced for speed)
        request_timeout (int): Timeout for the request in seconds
        _retry (bool): Internal flag to avoid infinite retries
    
    Returns:
        str: AI-generated response
    
    Raises:
        Exception: If there's an error generating the response
    """
    try:
        # Prepare the full prompt with context for better responses
        full_prompt = f"{NZ_UNIVERSITIES_CONTEXT}\n\nUser: {prompt}\nAINZUNI:"
        
        # Create request payload for Ollama with optimized parameters
        payload = {
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": False,  # Get complete response at once
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens,
                "top_k": 40,  # Added for faster generation
                "repeat_penalty": 1.1  # Added to prevent repetition
            }
        }
        
        logger.info(f"Sending request to Ollama: {payload['model']}")
        logger.info(f"Prompt length: {len(full_prompt)} characters")
        
        # Send request to Ollama API with configured timeout
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=request_timeout
        )
        
        logger.info(f"Ollama response status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse successful response
            result = response.json()
            response_text = result.get("response", "")
            
            if not response_text.strip():
                logger.warning("Empty response from Ollama")
                return "I apologize, but I couldn't generate a response at the moment. Please try again."
            
            logger.info(f"Generated response length: {len(response_text)} characters")
            return response_text
        else:
            # Handle API errors
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            raise Exception(f"Ollama API returned status {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        logger.error("Request to Ollama timed out")
        # Retry once with reduced tokens and extended timeout
        if not _retry:
            logger.info("Retrying once with reduced tokens and longer timeout...")
            reduced_tokens = max(100, int(max_tokens * 0.5))
            return generate_response(
                prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=reduced_tokens,
                request_timeout=max(request_timeout, 150),
                _retry=True
            )
        raise Exception("Request to Ollama timed out - the model may still be loading")
    except requests.exceptions.ConnectionError:
        logger.error("Connection error to Ollama")
        raise Exception("Cannot connect to Ollama - please ensure it's running")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with Ollama: {e}")
        raise Exception(f"Error communicating with Ollama: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise Exception(f"Unexpected error: {e}")

@app.route('/')
def index():
    """
    Serve the main chatbot interface.
    Returns: HTML content of the chatbot page
    """
    try:
        # Try to serve the HTML file from the AINZUNI Website directory
        html_path = os.path.join(os.path.dirname(__file__), 'AINZUNI Website', 'AINZUNI.html')
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Fallback HTML if file not found
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>AINZUNI - NZ Universities</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body>
                <h1>AINZUNI Chatbot</h1>
                <p>Please open the AINZUNI.html file directly in your browser or ensure the Flask server can find it.</p>
                <p>Server is running at: <a href="http://localhost:5000">http://localhost:5000</a></p>
            </body>
            </html>
            '''
    except Exception as e:
        logger.error(f"Error serving index: {e}")
        return f"Error loading page: {str(e)}", 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat requests from the frontend - OPTIMIZED FOR SPEED.
    This is the main endpoint that processes user messages and returns AI responses.
    
    Expected JSON input: {"message": "user's question"}
    Returns: JSON with AI response or error message
    """
    try:
        # Parse user message from request
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Use cached status check for faster response
        if not get_cached_ollama_status():
            return jsonify({
                "error": "Ollama not available",
                "message": "Please make sure Ollama is running and the llama3.1:8b model is installed."
            }), 503
        
        # Generate AI response using real Llama model with optimized parameters
        try:
            response = generate_response(user_message)
            return jsonify({
                "response": response,
                "model": MODEL_NAME
            })
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return jsonify({
                "error": "AI model error",
                "message": str(e)
            }), 500
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """
    Check the status of the Ollama connection.
    Returns: JSON with connection status and model info
    """
    ollama_available = get_cached_ollama_status()
    return jsonify({
        "ollama_available": ollama_available,
        "model": MODEL_NAME,
        "status": "running"
    })

@app.route('/api/models', methods=['GET'])
def list_models():
    """
    List available Ollama models.
    Returns: JSON with list of installed models
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)  # Reduced timeout
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Could not fetch models"}), 500
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        return jsonify({"error": "Could not connect to Ollama"}), 503

@app.route('/api/test', methods=['GET'])
def test_connection():
    """
    Test the connection to Ollama and provide detailed status.
    This endpoint is useful for debugging connection issues.
    Returns: JSON with detailed connection and model status
    """
    try:
        # Test basic connection to Ollama with reduced timeout
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)  # Reduced timeout
        
        if response.status_code == 200:
            # Parse available models
            data = response.json()
            models = data.get("models", [])
            model_names = [model.get("name", "") for model in models]
            
            return jsonify({
                "status": "success",
                "ollama_connected": True,
                "available_models": model_names,
                "target_model": MODEL_NAME,
                "target_model_available": MODEL_NAME in model_names,
                "ollama_url": OLLAMA_BASE_URL
            })
        else:
            return jsonify({
                "status": "error",
                "ollama_connected": False,
                "error": f"Ollama returned status {response.status_code}",
                "ollama_url": OLLAMA_BASE_URL
            }), 500
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            "status": "error",
            "ollama_connected": False,
            "error": "Cannot connect to Ollama - it may not be running",
            "ollama_url": OLLAMA_BASE_URL,
            "suggestion": "Run 'ollama serve' in a terminal"
        }), 503
    except Exception as e:
        return jsonify({
            "status": "error",
            "ollama_connected": False,
            "error": str(e),
            "ollama_url": OLLAMA_BASE_URL
        }), 500

if __name__ == '__main__':
    # STARTUP MESSAGES - Display server information
    print("Starting AINZUNI Llama Server - OPTIMIZED FOR SPEED...")
    print(f"Model: {MODEL_NAME}")
    print(f"Ollama URL: {OLLAMA_BASE_URL}")
    print(f"Optimizations: Reduced timeouts, cached status, optimized parameters")
    print(f"HTML file path: {os.path.join(os.path.dirname(__file__), 'AINZUNI Website', 'AINZUNI.html')}")
    
    # CHECK INITIAL STATUS - Verify Ollama and model availability
    print("\nChecking Ollama status...")
    if check_ollama_status():
        print("Ollama is running and model is available")
        
        # WARM UP MODEL - Pre-load model for faster responses
        print("\nWarming up model...")
        if warmup_model():
            print("Model is ready for use")
        else:
            print("Model warmup failed, but server will continue")
    else:
        print("Ollama is not available or model not found")
        print("   Please ensure:")
        print("   1. Ollama is installed: https://ollama.ai")
        print("   2. Ollama is running: ollama serve")
        print("   3. Model is downloaded: ollama pull llama3.1:8b")
    
    # DISPLAY SERVER INFORMATION
    print("\nServer will be available at: http://localhost:5000")
    print("API endpoints:")
    print("   - Chat: http://localhost:5000/api/chat")
    print("   - Status: http://localhost:5000/api/status")
    print("   - Test: http://localhost:5000/api/test")
    print("   - Models: http://localhost:5000/api/models")
    
    print("\nSpeed Optimizations:")
    print("   - Reduced timeouts for faster failure detection")
    print("   - Cached connection status checks")
    print("   - Optimized model parameters for speed")
    print("   - Reduced response length for faster generation")
    
    print("\nTroubleshooting:")
    print("   - If you see 'AI Model Not Available', check the test endpoint above")
    print("   - Make sure Ollama is running in a separate terminal")
    print("   - The first request may take longer as the model loads")
    
    # START FLASK SERVER - Run the web server
    app.run(host='0.0.0.0', port=5000, debug=True)
