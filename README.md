# AINZUNI - AI-Powered NZ Universities Chatbot

AINZUNI is an intelligent chatbot interface that provides information about New Zealand universities using locally hosted AI models via Ollama. The chatbot features a full-page interface and integrates with Ollama for real-time, private AI processing.

## 🌟 Features

- **Full-Page Chat Interface**: Modern, responsive design
- **Ollama Integration**: Supports any Ollama-compatible model (e.g., phi4:14b, Llama 3, etc.)
- **NZ Universities Specialization**: Expert knowledge about New Zealand's 8 universities
- **Real-time Responses**: Fast, intelligent answers from your local model
- **Dark/Light Theme**: Toggle for user comfort
- **Responsive Design**: Works on desktop, tablet, and mobile

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
- Ollama (for running local AI models, e.g., phi4:14b)
- Modern web browser

## 🚀 Quick Setup

### 1. Install Ollama and Your Model

- Download Ollama: [https://ollama.ai](https://ollama.ai)
- Install the desired model (example for phi4:14b):
  ```bash
  ollama pull phi4:14b
  ```
- Start Ollama:
  ```bash
  ollama serve
  ```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Chat Proxy Server

This server connects your website to Ollama securely.

```bash
python chat_proxy_example.py
```
- By default, it connects to Ollama at `http://localhost:11434` and uses the model name you specify (e.g., `phi4:14b`).

### 4. Serve the Website

```bash
python -m http.server 8001
```
- Open your browser to: [http://localhost:8001/AINZUNI.html](http://localhost:8001/AINZUNI.html)

### 5. Configure the Frontend Chat API (in browser console)

```javascript
localStorage.setItem('chat_api_url', 'http://127.0.0.1:8000/api/chat');
location.reload();
```

## 🎯 Usage

1. **Open the chatbot** in your browser
2. **Type your question** about NZ universities
3. **Press Enter** or click "Send" for an AI-powered response

## 💬 Example Questions

- "What are the admission requirements for University of Auckland?"
- "Tell me about computer science programs in New Zealand"
- "Which universities offer medicine degrees?"
- "What scholarships are available for international students?"
- "Compare the campuses of different NZ universities"

## 🛠️ Technical Details

### Architecture

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python Flask proxy server (`chat_proxy_example.py`)
- **AI Model**: Any Ollama-compatible model (e.g., phi4:14b, Llama 3, etc.)
- **API**: RESTful `/api/chat` endpoint

### File Structure

```
├── AINZUNI Website/
│   └── AINZUNI.html          # Main chatbot interface
│   └── chat_proxy_example.py # Python proxy server for Ollama
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

### API Endpoints

- `POST /api/chat` - Send message and get AI response (via Ollama)
- (Other endpoints may be added for status or model listing)

## 🔧 Configuration

### Environment Variables

Set these before starting the proxy server:

```bash
export MODEL_PROVIDER="ollama"
export MODEL_NAME="phi4:14b"           # Or your installed model name
export OLLAMA_API_URL="http://localhost:11434"  # Default Ollama API URL
```

### Model Parameters

You can adjust parameters in `chat_proxy_example.py` (temperature, max tokens, etc.).

## 🐛 Troubleshooting

### Common Issues

1. **"Ollama not available" error**:
   - Make sure Ollama is installed and running (`ollama serve`)
   - Check if the model is downloaded: `ollama list`

2. **"Proxy server not available" error**:
   - Ensure `chat_proxy_example.py` is running
   - Check if port 8000 is available

3. **"Model not found"**:
   - Download the model: `ollama pull phi4:14b`
   - Check available models: `ollama list`

4. **Connection refused**:
   - Make sure both Ollama and the proxy server are running
   - Serve the website via HTTP, not file://

### Performance Tips

- **Model Size**: Use smaller models for faster responses
- **Memory**: Ensure sufficient RAM (8GB+ recommended for large models)

## 🔒 Security

- All AI processing is local
- No data sent to external servers (except Ollama API calls)
- No user data stored or logged

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License

## 🙏 Acknowledgments

- **Ollama** for local AI inference
- **Meta AI** and other model providers
- **Flask** for the web framework
- **New Zealand Universities** for educational content

## 📞 Support

- Review the troubleshooting section above
- See Ollama docs: [https://ollama.ai/docs](https://ollama.ai/docs)
- Open an issue on the project repository

---

**Happy learning about New Zealand universities! 🎓🇳🇿**
