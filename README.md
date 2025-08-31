# AINZUNI — NZ Universities Chatbot

Lightweight local chatbot UI that uses Ollama-hosted models (e.g., phi4:14b) to answer questions about New Zealand universities.

## Prerequisites
- Python 3.8+
- Ollama installed and running
- Modern browser

## Quick start
1. Pull model and run Ollama:
```bash
ollama pull phi4:14b
ollama serve
```
2. Install Python deps:
```bash
pip install -r requirements.txt
```
3. Start the proxy (point to your Ollama model):
```powershell
$env:MODEL_PROVIDER='ollama'
$env:MODEL_NAME='phi4:14b'
.\.venv\Scripts\python.exe chat_proxy_example.py
```
4. Serve the site and open:
```bash
python -m http.server 8001
# Open http://127.0.0.1:8001/AINZUNI.html
```
5. Point frontend to proxy (browser console):
```javascript
localStorage.setItem('chat_api_url','http://127.0.0.1:8000/api/chat'); location.reload();
```

## Usage
Type questions about NZ universities and press Enter. Model replies are served from your local Ollama instance.

## Troubleshooting (brief)
- If proxy returns mock: restart proxy with MODEL_PROVIDER=ollama and correct MODEL_NAME.
- If connection refused: ensure Ollama (`localhost:11434`) and proxy (`localhost:8000`) are running and site served over HTTP.
- Check `ollama list` to confirm model name.

## License
MIT
