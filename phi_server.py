import os
import json
from typing import Iterator

import requests
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    default_model = os.environ.get("MODEL_NAME", "phi4:14b")

    @app.get("/api/status")
    def status():
        ok = True
        ollama_ok = False
        models = []
        try:
            tags_resp = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            if tags_resp.ok:
                ollama_ok = True
                tags = tags_resp.json().get("models", [])
                models = [m.get("name") for m in tags if m.get("name")]
        except Exception:
            ok = False
        return jsonify({
            "ok": ok and ollama_ok,
            "ollama_ok": ollama_ok,
            "ollama_base_url": ollama_base_url,
            "models": models,
            "default_model": default_model,
        })

    @app.get("/api/models")
    def list_models():
        try:
            tags_resp = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            tags_resp.raise_for_status()
            data = tags_resp.json()
            return jsonify(data)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 502

    @app.post("/api/chat")
    def chat_stream():
        try:
            payload = request.get_json(force=True, silent=False) or {}
        except BadRequest:
            return jsonify({"error": "Invalid JSON body"}), 400

        messages = payload.get("messages", [])
        model = payload.get("model") or default_model
        stream = payload.get("stream", True)
        options = payload.get("options") or {}

        if not isinstance(messages, list) or not messages:
            return jsonify({"error": "'messages' must be a non-empty list"}), 400

        upstream_url = f"{ollama_base_url}/api/chat"
        upstream_body = {
            "model": model,
            "messages": messages,
            "stream": True if stream else False,
        }
        if options:
            upstream_body["options"] = options

        headers = {"Content-Type": "application/json"}

        if stream:
            def generate() -> Iterator[str]:
                with requests.post(upstream_url, data=json.dumps(upstream_body), headers=headers, stream=True, timeout=(10, 600)) as r:
                    r.raise_for_status()
                    for line in r.iter_lines(decode_unicode=True):
                        if not line:
                            continue
                        # Forward NDJSON line-by-line to the client
                        yield line + "\n"

            return Response(generate(), mimetype="application/x-ndjson")
        else:
            try:
                r = requests.post(upstream_url, data=json.dumps(upstream_body), headers=headers, timeout=600)
                r.raise_for_status()
                return jsonify(r.json())
            except requests.RequestException as exc:
                return jsonify({"error": str(exc)}), 502

    @app.get("/")
    def root():
        return jsonify({
            "message": "AINZUNI Phi-4 backend is running",
            "endpoints": ["GET /api/status", "GET /api/models", "POST /api/chat"],
            "model": default_model,
        })

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("FLASK_PORT", "5000"))
    # threaded=True allows one request to stream while others still respond
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)

