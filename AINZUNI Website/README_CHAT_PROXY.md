AINZUNI Chat Proxy (example)

Purpose
- Provides a simple local proxy so the `AINZUNI.html` frontend can send chat messages without embedding API keys in the browser.
- Default behavior: if no MODEL_API_URL is set, the proxy responds with a mock echo reply for frontend testing.

How to run (Windows PowerShell)
1. Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate; pip install flask requests
```

2. (Optional) Configure environment variables to point to your model provider. Example for a generic provider:

```powershell
$env:MODEL_API_URL = 'https://your-model-provider.example.com/infer'
$env:MODEL_API_KEY = 'your-secret-key'
```

Hugging Face (phi4-14b) example
- If you have a Hugging Face Inference API key and want to call a hosted phi4-14b model, set these variables instead:

```powershell
$env:MODEL_PROVIDER = 'huggingface'
$env:MODEL_NAME = 'owner/phi4-14b'  # replace with the actual model name/path on Hugging Face
$env:MODEL_API_KEY = '<your-hf-inference-api-key>'
```

The proxy will call the Hugging Face inference endpoint and return a normalized { "reply": "..." } JSON object.

Ollama (local phi4-14b installed via Ollama)
- If you installed phi4-14b using Ollama and have the Ollama daemon running, point the proxy to use the Ollama local API:

```powershell
$env:MODEL_PROVIDER = 'ollama'
# optionally set MODEL_NAME or leave empty to use the model name from the payload
$env:MODEL_NAME = 'phi4-14b'
python chat_proxy_example.py
```

Ollama typically exposes a local HTTP API at http://127.0.0.1:11434. Ensure Ollama is running (e.g., `ollama serve` or your OS service). The proxy will forward the prompt to the Ollama endpoint and return the reply as { "reply": "..." }.

3. Run the proxy:

```powershell
python chat_proxy_example.py
```

4. Open `AINZUNI.html` in a browser and ensure CHAT_API_URL (in the page's script) points to `http://127.0.0.1:8000/api/chat`.

Notes
- For production, run a robust server (gunicorn/uvicorn) behind HTTPS and set appropriate CORS headers and authentication.
- The example proxy expects the upstream model to accept JSON like {model, input} and to return a JSON object containing a textual reply. Adjust `chat_proxy_example.py` if your provider uses a different request/response shape.
