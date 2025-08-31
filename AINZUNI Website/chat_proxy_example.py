"""Simple chat proxy example for the AINZUNI frontend.

- Run this locally and point the frontend CHAT_API_URL to http://127.0.0.1:8000/api/chat
- The proxy keeps API keys server-side and forwards requests to your model provider.
- Configure MODEL_API_URL and MODEL_API_KEY environment variables to call your model API.

This is intentionally generic: set MODEL_API_URL to whatever HTTP endpoint your provider expects
(e.g. a Hugging Face Inference API URL, a PhiLabs endpoint, or another hosted model endpoint).
If none is provided the proxy will return a predictable mock reply for testing.

Usage (PowerShell):
  python -m venv .venv; .\.venv\Scripts\Activate; pip install flask requests; python chat_proxy_example.py

"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)  # allow browser to call the local proxy during development

# Configuration via environment variables
# MODEL_PROVIDER: 'huggingface' or leave empty to use generic MODEL_API_URL
MODEL_PROVIDER = os.environ.get('MODEL_PROVIDER', '').lower()
MODEL_API_URL = os.environ.get('MODEL_API_URL')
MODEL_API_KEY = os.environ.get('MODEL_API_KEY')
MODEL_NAME = os.environ.get('MODEL_NAME')  # for huggingface, e.g. 'phi4/phi4-14b' or similar


@app.route('/api/chat', methods=['POST'])
def chat():
    payload = request.get_json(force=True)
    user_input = payload.get('input')
    model = payload.get('model')

    if not user_input:
        return jsonify({'error': 'input is required'}), 400

    # If provider is Hugging Face, call their Inference API
    if MODEL_PROVIDER == 'huggingface':
        if not MODEL_NAME:
            return jsonify({'error': 'MODEL_NAME environment variable required for huggingface provider'}), 500
        hf_url = f'https://api-inference.huggingface.co/models/{MODEL_NAME}'
        headers = {'Authorization': f'Bearer {MODEL_API_KEY}'} if MODEL_API_KEY else {}
        body = {
            'inputs': user_input,
            # you can tune generation parameters here
            'parameters': { 'max_new_tokens': 512 }
        }
        try:
            resp = requests.post(hf_url, json=body, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            # Hugging Face returns either {'generated_text': '...'} or a list of dicts
            reply = None
            if isinstance(data, dict):
                reply = data.get('generated_text') or data.get('text')
            elif isinstance(data, list) and len(data) > 0:
                first = data[0]
                if isinstance(first, dict):
                    reply = first.get('generated_text') or first.get('generated_text') or first.get('text')

            if not reply:
                reply = str(data)

            return jsonify({'reply': reply})
        except requests.RequestException as e:
            return jsonify({'error': 'upstream request failed', 'details': str(e)}), 502

    # Ollama local user installation (no API key required by default)
    if MODEL_PROVIDER == 'ollama':
        # Ollama default HTTP API listens on 127.0.0.1:11434
        ollama_url = os.environ.get('OLLAMA_API_URL', 'http://127.0.0.1:11434/api/generate')
        # prefer MODEL_NAME if provided, otherwise use model from payload or fallback
        model_to_use = MODEL_NAME or model or 'phi4-14b'
        body = {
            'model': model_to_use,
            'prompt': user_input,
            # set sensible defaults; adjust as needed
            'max_tokens': 512
        }
        try:
            resp = requests.post(ollama_url, json=body, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            # Try to extract a reply from common shapes
            reply = None
            if isinstance(data, dict):
                # Ollama often returns {"model":"...","response":"..."} or similar
                reply = data.get('response') or data.get('text') or data.get('result') or data.get('output')
                # sometimes wrapped in 'choices' or 'results'
                if not reply:
                    if isinstance(data.get('choices'), list) and len(data['choices'])>0:
                        first = data['choices'][0]
                        if isinstance(first, dict):
                            reply = first.get('text') or first.get('message') or first.get('content')
                    if not reply and isinstance(data.get('results'), list) and len(data['results'])>0:
                        first = data['results'][0]
                        if isinstance(first, dict):
                            reply = first.get('text') or first.get('content')
            if not reply and isinstance(data, list) and len(data)>0:
                first = data[0]
                if isinstance(first, dict):
                    reply = first.get('text') or first.get('content')
            if not reply:
                reply = str(data)

            return jsonify({'reply': reply})
        except requests.RequestException as e:
            return jsonify({'error': 'ollama request failed', 'details': str(e)}), 502

    # If a generic MODEL_API_URL is set, forward there
    if MODEL_API_URL:
        headers = {'Authorization': f'Bearer {MODEL_API_KEY}'} if MODEL_API_KEY else {}
        try:
            forward_body = {'model': model, 'input': user_input}
            resp = requests.post(MODEL_API_URL, json=forward_body, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            # Try to extract a reply from several common response shapes.
            reply = None
            if isinstance(data, dict):
                reply = data.get('reply') or data.get('output') or data.get('text')
                if not reply and 'generated_text' in data:
                    reply = data['generated_text']
                if not reply:
                    if isinstance(data.get('outputs'), list) and len(data['outputs']) > 0:
                        first = data['outputs'][0]
                        if isinstance(first, dict):
                            reply = first.get('generated_text') or first.get('text')
            if not reply and isinstance(data, list) and len(data) > 0:
                first = data[0]
                if isinstance(first, dict):
                    reply = first.get('generated_text') or first.get('text')
            if not reply:
                reply = str(data)

            return jsonify({'reply': reply})
        except requests.RequestException as e:
            return jsonify({'error': 'upstream request failed', 'details': str(e)}), 502

    # No upstream configured: return mock reply for frontend testing
    return jsonify({'reply': f"(mock) Echoing to {model}: {user_input}"})


if __name__ == '__main__':
    # Use 127.0.0.1 to avoid exposing the server by default
    app.run(host='127.0.0.1', port=8000, debug=True)
