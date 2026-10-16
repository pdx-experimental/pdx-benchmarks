from datetime import datetime
def parse(value):
    d = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if d.utcoffset() is None: raise ValueError('timezone required')
    return d
def run(payload):
    start, end = parse(payload['start']), parse(payload['end'])
    return {'events': [x for x in payload['events'] if start < parse(x) < end]}
