#!/usr/bin/env python3
"""
Test script to verify Flask server functionality
This script tests the complete Flask server setup: connection, startup, and chat functionality.
"""

import requests
import time
import subprocess
import sys
import os

def test_flask_server():
    """
    Test if Flask server is running and responding.
    This function checks if the Flask server is accessible and responding to requests.
    
    Returns:
        bool: True if server is running, False otherwise
    """
    print("🔍 Testing Flask server...")
    
    try:
        # Test if server is running by calling the test endpoint
        response = requests.get("http://localhost:5000/api/test", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Flask server is running")
            print(f"📊 Server response: {data}")
            return True
        else:
            print(f"❌ Flask server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask server is not running")
        return False
    except Exception as e:
        print(f"❌ Error testing Flask server: {e}")
        return False

def start_flask_server():
    """
    Start the Flask server in background.
    This function launches the Flask server as a subprocess and waits for it to start.
    
    Returns:
        subprocess.Popen or None: Process object if successful, None if failed
    """
    print("🚀 Starting Flask server...")
    try:
        # Start the server in background using subprocess
        process = subprocess.Popen([sys.executable, "llama_server.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Flask server started successfully")
            return process
        else:
            # Process failed to start, get error output
            stdout, stderr = process.communicate()
            print(f"❌ Flask server failed to start")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"❌ Error starting Flask server: {e}")
        return None

def test_chat_endpoint():
    """
    Test the chat endpoint.
    This function sends a test message to verify the chat functionality is working.
    
    Returns:
        bool: True if chat endpoint works, False otherwise
    """
    print("\n💬 Testing chat endpoint...")
    try:
        # Send a test message to the chat endpoint
        response = requests.post("http://localhost:5000/api/chat", 
                               json={"message": "Hello, test message"},
                               timeout=30)
        
        if response.status_code == 200:
            # Parse and display the response
            data = response.json()
            print("✅ Chat endpoint working")
            print(f"📝 Response: {data.get('response', 'No response')[:100]}...")
            return True
        else:
            print(f"❌ Chat endpoint failed (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing chat endpoint: {e}")
        return False

def main():
    """
    Run all tests in sequence.
    This function orchestrates the complete testing process.
    """
    print("🧪 Flask Server Test")
    print("=" * 50)
    
    # Test if server is already running
    if test_flask_server():
        print("\n✅ Flask server is already running")
    else:
        print("\n🔄 Starting Flask server...")
        process = start_flask_server()
        if not process:
            print("❌ Failed to start Flask server")
            sys.exit(1)
        
        # Wait a bit more for server to fully start
        time.sleep(2)
        
        # Test server again
        if not test_flask_server():
            print("❌ Flask server is not responding")
            sys.exit(1)
    
    # Test chat endpoint functionality
    if test_chat_endpoint():
        print("\n🎉 All tests passed!")
        print("✅ Flask server is working correctly")
        print("✅ Chat endpoint is responding")
        print("\nYou can now use the chatbot interface!")
    else:
        print("\n❌ Chat endpoint test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
