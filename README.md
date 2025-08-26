# AINZUNI - AI-Powered NZ Universities Chatbot

AINZUNI is an intelligent chatbot interface that provides information about New Zealand universities using Llama 3.1:8b. The chatbot features a full-page interface and integrates with Ollama for local AI processing.

## 🌟 Features

- **Full-Page Chat Interface**: Modern, responsive design that fills the entire page
- **Llama 3.1:8b Integration**: Powered by Meta's latest language model
- **NZ Universities Specialization**: Expert knowledge about New Zealand's 8 universities
- **Real-time Responses**: Fast, intelligent responses to user queries
- **Dark/Light Theme**: Toggle between themes for better user experience
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🏫 Supported Universities

- University of Auckland
- University of Otago
- Victoria University of Wellington
- University of Canterbury
- Massey University
- University of Waikato
- Lincoln University
- Auckland University of Technology

## 📋 Prerequisites

- Python 3.8 or higher
- Ollama (for running Llama 3.1:8b locally)
- Modern web browser

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

1. **Run the setup script**:
   ```bash
   python setup.py
   ```

2. **Start the server**:
   ```bash
   python llama_server.py
   ```

3. **Open your browser** to `http://localhost:5000`

### Option 2: Manual Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Ollama**:
   - Visit [https://ollama.ai](https://ollama.ai)
   - Download and install for your operating system

3. **Download Llama 3.1:8b model**:
   ```bash
   ollama pull llama3.1:8b
   ```

4. **Start Ollama service**:
   ```bash
   ollama serve
   ```

5. **Start the Flask server**:
   ```bash
   python llama_server.py
   ```

6. **Open your browser** to `http://localhost:5000`

## 🎯 Usage

1. **Open the chatbot** in your web browser
2. **Type your question** about NZ universities in the chat input
3. **Press Enter** or click "Send" to get an AI-powered response
4. **Toggle themes** using the moon/sun button in the top-right corner
5. **Navigate** using the menu button in the top-left corner

## 💬 Example Questions

- "What are the admission requirements for University of Auckland?"
- "Tell me about computer science programs in New Zealand"
- "Which universities offer medicine degrees?"
- "What scholarships are available for international students?"
- "Compare the campuses of different NZ universities"

## 🛠️ Technical Details

### Architecture

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask server
- **AI Model**: Llama 3.1:8b via Ollama
- **API**: RESTful API with JSON responses

### File Structure

```
├── AINZUNI Website/
│   └── AINZUNI.html          # Main chatbot interface
├── llama_server.py           # Flask backend server
├── requirements.txt          # Python dependencies
├── setup.py                  # Automated setup script
├── start_ainzuni.sh         # Startup script (Unix/Linux)
└── README.md                # This file
```

### API Endpoints

- `GET /` - Main chatbot interface
- `POST /api/chat` - Send message and get AI response
- `GET /api/status` - Check server and Ollama status
- `GET /api/models` - List available Ollama models

## 🔧 Configuration

### Environment Variables

You can customize the server behavior by setting these environment variables:

```bash
export OLLAMA_BASE_URL="http://localhost:11434"  # Ollama server URL
export MODEL_NAME="llama3.1:8b"                  # AI model name
export FLASK_PORT=5000                           # Flask server port
```

### Model Parameters

The AI model parameters can be adjusted in `llama_server.py`:

```python
DEFAULT_TEMPERATURE = 0.7    # Creativity (0.0-1.0)
DEFAULT_TOP_P = 0.9          # Response diversity
DEFAULT_MAX_TOKENS = 500     # Maximum response length
```

## 🐛 Troubleshooting

### Common Issues

1. **"Ollama not available" error**:
   - Make sure Ollama is installed and running
   - Run `ollama serve` in a separate terminal
   - Check if the model is downloaded: `ollama list`

2. **"Flask server not available" error**:
   - Ensure the Flask server is running: `python llama_server.py`
   - Check if port 5000 is available
   - Try a different port if needed

3. **Slow responses**:
   - The first response may be slow as the model loads
   - Subsequent responses should be faster
   - Consider using a smaller model for faster responses

4. **Model not found**:
   - Download the model: `ollama pull llama3.1:8b`
   - Check available models: `ollama list`

### Performance Tips

- **GPU Acceleration**: Install CUDA drivers for faster inference
- **Model Size**: Consider using smaller models for faster responses
- **Memory**: Ensure sufficient RAM (8GB+ recommended for 8B models)

## 🔒 Security

- The chatbot runs locally on your machine
- No data is sent to external servers (except Ollama API calls)
- All conversations are processed locally
- No user data is stored or logged

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Meta AI** for Llama 3.1:8b
- **Ollama** for the local AI inference framework
- **Flask** for the web framework
- **New Zealand Universities** for the educational content

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the Ollama documentation: [https://ollama.ai/docs](https://ollama.ai/docs)
3. Open an issue on the project repository

---

**Happy learning about New Zealand universities! 🎓🇳🇿**
