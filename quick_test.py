#!/usr/bin/env python3
"""
Quick test script to verify basic chat functionality
This script provides a fast way to test if the chat system is working.
"""

import requests

# Quick test with shorter timeout
try:
    # Send a simple "Hello" message to test the chat endpoint
    response = requests.post(
        "http://localhost:5000/api/chat",
        json={"message": "Hello"},
        timeout=30  # 30-second timeout for quick testing
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        # Successfully received response
        data = response.json()
        print(f"Response: {data.get('response', 'No response')[:100]}...")
    else:
        # Error occurred
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")
