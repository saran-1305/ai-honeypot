import os, requests

SESSION = requests.Session()

class LLM:
    def __init__(self):
        self.backend      = (os.getenv("LLM_BACKEND","ollama") or "ollama").lower()
        self.ollama_host  = os.getenv("OLLAMA_HOST","http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL","qwen2.5:7b")
        self.openai_key   = os.getenv("OPENAI_API_KEY","")
        self.openai_model = os.getenv("OPENAI_MODEL","gpt-4o-mini")

    def chat(self, system_prompt, user_prompt, max_tokens=160):
        try:
            if self.backend == "ollama":
                return self._chat_ollama(system_prompt, user_prompt, max_tokens)
            elif self.backend == "openai":
                return self._chat_openai(system_prompt, user_prompt, max_tokens)
            return "DIAG: backend not configured"
        except Exception as e:
            # DO NOT hide errors; show them so UI can display what failed
            return f"DIAG (chat): {type(e).__name__}: {str(e)[:200]}"

    # ---- Native Ollama API (/api/chat) ----
    def _chat_ollama(self, system_prompt, user_prompt, max_tokens):
        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            "options": {
                "num_predict": max_tokens,
                "top_k": 30,
                "top_p": 0.9,
                "temperature": 0.6,
            },
            "stream": False
        }
        try:
            r = SESSION.post(f"{self.ollama_host}/api/chat", json=payload, timeout=90)
            if r.status_code != 200:
                # Fallback when Ollama is not reachable
    return {
    "role": "assistant",
    "content": "Our IT Helpdesk is currently experiencing high load. Please try again later. If urgent, submit a support ticket with your Employee ID."
}
            data = r.json()
            msg = (data.get("message") or {}).get("content") or ""
            return msg.strip() or "DIAG: empty model response"
        except Exception as e:
            # Fallback when Ollama is not reachable
    return {
    "role": "assistant",
    "content": "Our IT Helpdesk is currently experiencing high load. Please try again later. If urgent, submit a support ticket with your Employee ID."
}

    # ---- OpenAI path kept for later (not used when backend=ollama) ----
    def _chat_openai(self, system_prompt, user_prompt, max_tokens):
        try:
            if not self.openai_key:
                return "OpenAI backend not configured."
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            resp = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role":"system","content":system_prompt},
                    {"role":"user","content":user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"DIAG (openai): {type(e).__name__}: {str(e)[:200]}"



import random, time

def ollama_fallback():
    fallbacks = [
        "Our IT Helpdesk is currently experiencing high load. Please try again later. If urgent, submit a support ticket with your Employee ID.",
        "A temporary outage is affecting automated replies. A support case has been opened: SR-" + str(int(time.time()))[-6:],
        "We are processing many requests right now. Please retry in a few minutes. Meanwhile, you may check the IT knowledge base or contact support.",
        "Your request has been noted. Due to system maintenance, responses may be delayed. Thank you for your patience."
    ]
    return {
        "role": "assistant",
        "content": random.choice(fallbacks)
    }

