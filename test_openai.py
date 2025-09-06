from openai import OpenAI
import os

print("has_key:", bool(os.getenv("OPENAI_API_KEY")))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
r = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say ok"}],
    max_tokens=5
)
print("OK:", r.choices[0].message.content)
