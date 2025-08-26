#!/usr/bin/env python3
"""
AINZUNI Setup Script
This script helps set up the environment for the AINZUNI chatbot with Llama 3.1:8b integration.
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_python_dependencies():
    """Install Python dependencies."""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def check_ollama_installation():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        return False

def install_ollama():
    """Install Ollama based on the operating system."""
    system = platform.system().lower()
    
    if system == "windows":
        print("📥 Installing Ollama on Windows...")
        print("Please visit https://ollama.ai/download and download the Windows installer")
        print("After installation, restart your terminal and run this script again")
        return False
    elif system == "darwin":  # macOS
        return run_command(
            "curl -fsSL https://ollama.ai/install.sh | sh",
            "Installing Ollama on macOS"
        )
    elif system == "linux":
        return run_command(
            "curl -fsSL https://ollama.ai/install.sh | sh",
            "Installing Ollama on Linux"
        )
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False

def pull_llama_model():
    """Pull the Llama 3.1:8b model."""
    return run_command(
        "ollama pull llama3.1:8b",
        "Downloading Llama 3.1:8b model"
    )

def create_startup_script():
    """Create a startup script for easy launching."""
    script_content = """#!/bin/bash
# AINZUNI Startup Script

echo "🚀 Starting AINZUNI Chatbot with Llama 3.1:8b..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Start the server
echo "🌐 Starting Flask server..."
python llama_server.py
"""

    with open("start_ainzuni.sh", "w") as f:
        f.write(script_content)
    
    # Make executable on Unix-like systems
    if platform.system() != "windows":
        os.chmod("start_ainzuni.sh", 0o755)
    
    print("✅ Created startup script: start_ainzuni.sh")

def main():
    """Main setup function."""
    print("🎓 AINZUNI Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Check Ollama installation
    if not check_ollama_installation():
        print("\n📥 Ollama is not installed. Installing now...")
        if not install_ollama():
            print("❌ Failed to install Ollama")
            print("Please install Ollama manually from https://ollama.ai")
            sys.exit(1)
    
    # Pull Llama model
    print("\n📚 Setting up Llama 3.1:8b model...")
    if not pull_llama_model():
        print("❌ Failed to download Llama model")
        print("You can try running 'ollama pull llama3.1:8b' manually")
        sys.exit(1)
    
    # Create startup script
    create_startup_script()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the server: python llama_server.py")
    print("2. Open your browser to: http://localhost:5000")
    print("3. Or use the startup script: ./start_ainzuni.sh")
    print("\n💡 Tips:")
    print("- Make sure Ollama is running: ollama serve")
    print("- The model will be downloaded automatically on first use")
    print("- Check server status: http://localhost:5000/api/status")

if __name__ == "__main__":
    main()
