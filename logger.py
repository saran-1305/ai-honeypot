import os, json, uuid
from datetime import datetime

LOG_PATH = os.getenv("LOG_PATH", "logs/events.jsonl")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def log_event(event_type, **fields):
    record = {"ts": datetime.utcnow().isoformat()+"Z","event":event_type,**fields}
    with open(LOG_PATH,"a",encoding="utf-8") as f:
        f.write(json.dumps(record)+"\\n")

def new_correlation_id():
    return str(uuid.uuid4())
