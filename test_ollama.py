#!/usr/bin/env python3
"""
Test script to verify Ollama connection and model availability
This script tests the complete setup: Ollama connection, model availability, and model generation.
"""

import requests
import json
import sys

# CONFIGURATION - Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"  # Ollama API endpoint
MODEL_NAME = "llama3.1:8b"                  # Target model to test

def test_ollama_connection():
    """
    Test basic connection to Ollama.
    This function checks if Ollama is running and responding to API requests.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    print("🔍 Testing Ollama connection...")
    try:
        # Send GET request to Ollama's tags endpoint
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        print(f"✅ Connection successful (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
        print("   Please ensure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_model_availability():
    """
    Test if the required model is available.
    This function checks if the target model is installed and ready to use.
    
    Returns:
        bool: True if model is available, False otherwise
    """
    print("\n📚 Checking model availability...")
    try:
        # Get list of available models from Ollama
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if response.status_code == 200:
            # Parse the response to get model names
            data = response.json()
            models = data.get("models", [])
            model_names = [model.get("name", "") for model in models]
            
            print(f"Available models: {model_names}")
            
            # Check if our target model is in the list
            if MODEL_NAME in model_names:
                print(f"✅ Model '{MODEL_NAME}' is available")
                return True
            else:
                print(f"❌ Model '{MODEL_NAME}' is not available")
                print(f"   Please install it: ollama pull {MODEL_NAME}")
                return False
        else:
            print(f"❌ Failed to get models (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False

def test_model_generation():
    """
    Test if the model can generate responses.
    This function sends a test prompt to verify the model is working correctly.
    
    Returns:
        bool: True if model generates response successfully, False otherwise
    """
    print("\n🤖 Testing model generation...")
    try:
        # Create test payload for model generation
        payload = {
            "model": MODEL_NAME,
            "prompt": "Hello, can you respond with 'Test successful'?",
            "stream": False,  # Get complete response at once
            "options": {
                "temperature": 0.7,  # Controls randomness
                "top_p": 0.9,       # Controls diversity
                "num_predict": 50   # Maximum tokens to generate
            }
        }
        
        print("Sending test request...")
        # Send generation request to Ollama
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=60  # 1-minute timeout for generation
        )
        
        if response.status_code == 200:
            # Parse and display the response
            result = response.json()
            response_text = result.get("response", "")
            print(f"✅ Model response: {response_text}")
            return True
        else:
            print(f"❌ Model generation failed (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing model generation: {e}")
        return False

def main():
    """
    Run all tests in sequence.
    This function orchestrates the testing process and provides clear feedback.
    """
    print("🧪 Ollama Connection Test")
    print("=" * 50)
    
    # Test 1: Basic connection to Ollama
    if not test_ollama_connection():
        print("\n❌ Basic connection failed. Please fix this first.")
        sys.exit(1)
    
    # Test 2: Model availability check
    if not test_model_availability():
        print("\n❌ Model not available. Please install it first.")
        sys.exit(1)
    
    # Test 3: Model generation capability
    if not test_model_generation():
        print("\n❌ Model generation failed.")
        sys.exit(1)
    
    # All tests passed
    print("\n🎉 All tests passed!")
    print("✅ Ollama is working correctly")
    print("✅ Model is available and responding")
    print("\nYou can now run the Flask server: python llama_server.py")

if __name__ == "__main__":
    main()
