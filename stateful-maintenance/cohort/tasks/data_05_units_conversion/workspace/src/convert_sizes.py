def run(payload):
    units = {'B':1,'KiB':1024,'MiB':1000000}
    if payload['unit'] not in units: return {'error':'unknown_unit'}
    return {'bytes':payload['value'] * units[payload['unit']]}
