import json
from pathlib import Path
def run(payload):
    c = json.loads(Path('config/queues.json').read_text())
    if payload['success']: return {'action':'ack','metric':None}
    if payload['attempts'] <= c['max_attempts']: return {'action':'retry','metric':None}
    return {'action':c['dead_letter'],'metric':c['failure_metric']}
