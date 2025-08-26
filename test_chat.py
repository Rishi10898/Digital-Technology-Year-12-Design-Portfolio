#!/usr/bin/env python3
"""
Test script to verify chat functionality
This script tests the complete chat pipeline: sending messages and receiving AI responses.
"""

import requests
import json

def test_chat():
    """
    Test the chat endpoint.
    This function sends a test message and verifies the AI response.
    
    Returns:
        bool: True if chat functionality works, False otherwise
    """
    print("🧪 Testing Chat Functionality")
    print("=" * 50)
    
    try:
        # Test message about University of Auckland
        test_message = "Hello, tell me about University of Auckland"
        print(f"📝 Sending message: {test_message}")
        
        # Send request to chat endpoint
        response = requests.post(
            "http://localhost:5000/api/chat",
            json={"message": test_message},
            timeout=60  # 1-minute timeout for AI response
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse the response
            data = response.json()
            if "response" in data:
                # Successfully received AI response
                print("✅ Chat endpoint working!")
                print(f"🤖 AI Response: {data['response'][:200]}...")
                print(f"📚 Model used: {data.get('model', 'Unknown')}")
                return True
            elif "error" in data:
                # AI returned an error
                print(f"❌ AI Error: {data.get('message', data.get('error', 'Unknown error'))}")
                return False
        else:
            # HTTP error occurred
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Run the chat test and provide feedback
    if test_chat():
        print("\n🎉 Chat functionality is working correctly!")
        print("✅ You can now use the chatbot interface!")
    else:
        print("\n❌ Chat functionality test failed")
        print("Please check the Flask server and Ollama status")
