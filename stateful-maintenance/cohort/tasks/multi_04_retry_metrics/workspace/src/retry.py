import json
from pathlib import Path
def run(payload):
    n = min(payload['max_attempts'],payload['success_on']) if payload.get('success_on') is not None else payload['max_attempts']
    metric = json.loads(Path('config/metrics.json').read_text())['retry']
    return {'attempts':n,'retry_count':n,'metric':metric}
