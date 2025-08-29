import os
import json
import logging
from typing import Iterator, Any

import requests
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    default_model = os.environ.get("MODEL_NAME", "phi4:14b")
    # Use a single requests Session for keep-alive and pooling
    session = requests.Session()
    log = logging.getLogger("phi_server")
    log.setLevel(logging.INFO)

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

    @app.route("/api/chat", methods=["POST"])
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
        # Build upstream body: for streaming keep messages, for non-stream prefer a single prompt string
        if stream:
            upstream_body = {
                "model": model,
                "messages": messages,
                "stream": True,
            }
        else:
            # Build a simple prompt from the provided messages (system/user roles)
            parts = []
            for m in messages:
                role = m.get("role", "user")
                content = m.get("content", "")
                if not content:
                    continue
                if role == "system":
                    parts.append(f"System: {content}")
                elif role == "user":
                    parts.append(f"User: {content}")
                else:
                    parts.append(content)
            prompt = "\n".join(parts) or ""
            upstream_body = {
                "model": model,
                "prompt": prompt,
                "stream": False,
            }
        if options:
            upstream_body["options"] = options

        headers = {"Content-Type": "application/json"}

        # If the client requested a stream, proxy NDJSON through as before.
        if stream:
            def generate() -> Iterator[str]:
                with session.post(upstream_url, data=json.dumps(upstream_body), headers=headers, stream=True, timeout=(10, 600)) as r:
                    r.raise_for_status()
                    for line in r.iter_lines(decode_unicode=True):
                        if not line:
                            continue
                        # Forward NDJSON line-by-line to the client
                        yield line + "\n"

            return Response(generate(), mimetype="application/x-ndjson")

        # Non-streaming: return a simple JSON object { reply: "..." } to the client.
        try:
            r = session.post(upstream_url, data=json.dumps(upstream_body), headers=headers, timeout=600)
        except requests.RequestException as exc:
            log.exception("Upstream request failed (network)")
            if os.environ.get("MOCK_REPLY", "false").lower() in ("1", "true", "yes"):
                last_user = (messages[-1].get("content", "") if messages else "")
                mock = f"[MOCK REPLY] Received: {last_user}. Start your Ollama/phi4 server for real answers."
                return jsonify({"reply": mock})
            return jsonify({"error": "Upstream network error", "details": str(exc)}), 502

        # If upstream returned non-2xx, forward the body so clients can see exact reason.
        if not r.ok:
            body_text = r.text
            status = r.status_code
            log.warning("Upstream returned status %s: %s", status, body_text[:400])

            # If upstream failed with server error (5xx) and we sent 'messages', try a fallback using 'prompt'
            if 500 <= status < 600 and isinstance(messages, list) and messages:
                try:
                    # Build a simple prompt string from recent user/system messages
                    parts = []
                    for m in messages:
                        role = m.get("role", "user")
                        content = m.get("content", "")
                        if not content:
                            continue
                        if role == "system":
                            parts.append(f"System: {content}")
                        elif role == "user":
                            parts.append(f"User: {content}")
                        else:
                            parts.append(content)
                    prompt = "\n".join(parts)
                    fallback_body = {"model": model, "prompt": prompt, "stream": False}
                    log.info("Attempting fallback with plain prompt to Ollama")
                    rf = session.post(upstream_url, data=json.dumps(fallback_body), headers=headers, timeout=600)
                    if rf.ok:
                        try:
                            upstream_json = rf.json()
                        except Exception:
                            upstream_json = {"response_text": rf.text}

                        # Extract text as before
                        def extract_text(obj: Any) -> str:
                            if isinstance(obj, str):
                                return obj
                            if isinstance(obj, dict):
                                for key in ("response", "text", "content", "output"):
                                    if key in obj and isinstance(obj[key], str):
                                        return obj[key]
                                if "choices" in obj and isinstance(obj["choices"], list) and obj["choices"]:
                                    first = obj["choices"][0]
                                    if isinstance(first, dict):
                                        for k in ("message", "text", "content", "delta", "output"):
                                            if k in first:
                                                val = first[k]
                                                if isinstance(val, str):
                                                    return val
                                                if isinstance(val, dict):
                                                    for kk in ("content", "text", "response"):
                                                        if kk in val and isinstance(val[kk], str):
                                                            return val[kk]
                            if isinstance(obj, list) and obj:
                                return extract_text(obj[0])
                            return ""

                        reply_text = extract_text(upstream_json) or rf.text
                        return jsonify({"reply": reply_text})
                    else:
                        log.warning("Fallback also failed: %s %s", rf.status_code, rf.text[:400])
                except Exception:
                    log.exception("Fallback attempt failed")

            # Return upstream status and body to client for debugging
            return jsonify({"error": "Upstream error", "status": status, "body": body_text}), 502

        # upstream OK path
        try:
            upstream_json = r.json()
        except Exception:
            upstream_json = {"response_text": r.text}

        def extract_text(obj: Any) -> str:
            if isinstance(obj, str):
                return obj
            if isinstance(obj, dict):
                for key in ("response", "text", "content", "output"):
                    if key in obj and isinstance(obj[key], str):
                        return obj[key]
                if "choices" in obj and isinstance(obj["choices"], list) and obj["choices"]:
                    first = obj["choices"][0]
                    if isinstance(first, dict):
                        for k in ("message", "text", "content", "delta", "output"):
                            if k in first:
                                val = first[k]
                                if isinstance(val, str):
                                    return val
                                if isinstance(val, dict):
                                    for kk in ("content", "text", "response"):
                                        if kk in val and isinstance(val[kk], str):
                                            return val[kk]
            if isinstance(obj, list) and obj:
                return extract_text(obj[0])
            return ""

        reply_text = extract_text(upstream_json) or r.text
        return jsonify({"reply": reply_text})

    # Helpful GET handler so visiting the endpoint in a browser doesn't return 405
    @app.route("/api/chat", methods=["GET"])
    def chat_get_info():
        return jsonify({
            "message": "This endpoint accepts POST requests with a JSON body.\nExample: { \"messages\": [{ \"role\": \"user\", \"content\": \"Your question\" }], \"stream\": false }"
        })

    @app.route("/api/debug_call", methods=["POST"])
    def debug_call():
        """Directly call the upstream Ollama /api/chat with the given JSON body and
        return a detailed wrapper containing upstream status, headers and body.
        Use this to see the exact upstream error when debugging 500s.
        """
        try:
            payload = request.get_json(force=True, silent=False) or {}
        except BadRequest:
            return jsonify({"error": "Invalid JSON body"}), 400

        upstream_url = f"{ollama_base_url}/api/chat"
        headers = {"Content-Type": "application/json"}

        try:
            r = session.post(upstream_url, data=json.dumps(payload), headers=headers, timeout=60)
        except requests.RequestException as exc:
            return jsonify({"error": "network", "details": str(exc)}), 502

        # Build header dict
        try:
            hdrs = {k: v for k, v in r.headers.items()}
        except Exception:
            hdrs = {}

        # Try to parse JSON body, otherwise return as text (truncated to 20k)
        body_text = r.text or ""
        parsed = None
        try:
            parsed = r.json()
        except Exception:
            parsed = None

        return jsonify({
            "upstream_status": r.status_code,
            "upstream_headers": hdrs,
            "upstream_body_text_truncated": body_text[:20000],
            "upstream_body_json": parsed,
        }), (502 if not r.ok else 200)

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

