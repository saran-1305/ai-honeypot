import os
import json
import requests

class LLM:
    @staticmethod
    def ask(prompt: str) -> str:
        prompt = (prompt or "").strip()
        if not prompt:
            return "Please provide a question."

        backend = os.environ.get("LLM_BACKEND", "ollama").lower()

        if backend == "ollama":
            host = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434").rstrip("/")
            model = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
            url = f"{host}/api/generate"
            try:
                resp = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    }),
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()
                # Ollama returns {"response": "..."}
                return (data.get("response") or "").strip() or "No response from model."
            except Exception as e:
                # Surface a concise error; app.py will catch and format it
                raise RuntimeError(f"Ollama error: {e}")

        elif backend == "openai":
            # Optional: only used if OPENAI_API_KEY and OPENAI_MODEL are provided
            import openai  # requires openai in requirements.txt
            key = os.environ.get("OPENAI_API_KEY")
            model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
            if not key:
                raise RuntimeError("OPENAI_API_KEY not set.")
            try:
                client = openai.OpenAI(api_key=key)
                chat = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a concise helpdesk assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                return chat.choices[0].message.content.strip()
            except Exception as e:
                raise RuntimeError(f"OpenAI error: {e}")

        else:
            # Fallback: echo
            return f"(debug) backend={backend} prompt={prompt}"
