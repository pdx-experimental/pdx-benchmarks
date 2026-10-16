import json
from pathlib import Path

def run(payload):
    config = json.loads(Path("config/client.json").read_text())
    return {"timeout": config.get("timeout", 60), "retries": config["retries"]}
