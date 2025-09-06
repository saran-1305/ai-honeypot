import os, time, json, requests

class LLM:
    def __init__(self):
        # Which backend to use: 'ollama' (default) or 'openai'
        self.backend = (os.getenv("LLM_BACKEND", "ollama") or "ollama").lower()

        # Ollama settings
        self.ollama_host  = (os.getenv("OLLAMA_HOST", "http://localhost:11434") or "http://localhost:11434").rstrip("/")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

        # OpenAI settings
        self.openai_key   = (os.getenv("OPENAI_API_KEY", "") or "").strip()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def chat(self, system_prompt, user_prompt, max_tokens=120):
        if self.backend == "openai":
            return self._chat_openai(system_prompt, user_prompt, max_tokens)
        # default to ollama
        return self._chat_ollama(system_prompt, user_prompt, max_tokens)

    # ---------- OLLAMA ----------
    def _chat_ollama(self, system_prompt, user_prompt, max_tokens):
        url = f"{self.ollama_host}/api/chat"
        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            "stream": False,
            "options": { "num_predict": max(50, min(int(max_tokens), 240)), "top_k": 30, "top_p": 0.9, "temperature": 0.6 },
            "keep_alive": "30m",
        }
        try:
            r = requests.post(url, json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
            # Ollama may return {"message":{"content":"..."} } or {"response":"..."}
            return (data.get("message") or {}).get("content") or data.get("response") or "No answer."
        except Exception as e:
            return f"DIAG (ollama): {type(e).__name__}: {str(e)[:200]}"

    # ---------- OPENAI ----------
    def _chat_openai(self, system_prompt, user_prompt, max_tokens):
        if not self.openai_key:
            return "OpenAI backend not configured. Please set OPENAI_API_KEY."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)  # no proxies kwarg
            resp = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"DIAG (openai): {type(e).__name__}: {str(e)[:200]}"
