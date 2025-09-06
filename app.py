import os, json, time, pathlib, traceback
from flask import Flask, request, jsonify
from llm_adapter import LLM

app = Flask(__name__)
pathlib.Path("/logs").mkdir(parents=True, exist_ok=True)

@app.route("/")
def home():
    return "<h3>AI Honeypot</h3><p>OK</p>"

@app.route("/health")
def health():
    return jsonify({"ok": True})

@app.route("/diag2")
def diag2():
    return jsonify({
        "backend": os.environ.get("LLM_BACKEND", "ollama"),
        "has_openai_key": bool(os.environ.get("OPENAI_API_KEY")),
        "ollama_host": os.environ.get("OLLAMA_HOST"),
        "ollama_model": os.environ.get("OLLAMA_MODEL"),
        "openai_model": os.environ.get("OPENAI_MODEL"),
    })

@app.route("/helpdesk", methods=["POST"])
def helpdesk():
    data = request.get_json(force=True) or {}
    q = data.get("q", "").strip()
    ip = request.remote_addr or "?"
    answer = None
    err = None

    try:
        answer = LLM.ask(q)
        return jsonify({"answer": answer})
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        # Return a 502 to indicate upstream (LLM) failure but keep API alive
        return jsonify({"error": "llm_failed", "detail": err}), 502
    finally:
        # Always log what happened
        try:
            with open("/logs/helpdesk.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "ts": time.time(),
                    "ip": ip,
                    "q": q,
                    "ans": answer,
                    "error": err,
                }) + "\n")
        except Exception:
            # Last resort: don't crash on logging errors
            pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8088)))
