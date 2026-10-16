from datetime import datetime, timezone
def run(payload):
    d = datetime.fromisoformat(payload['timestamp'].replace('Z','+00:00'))
    if d.utcoffset() is None: raise ValueError('naive timestamp')
    return {'timestamp':d.isoformat().replace('+00:00','Z')}
