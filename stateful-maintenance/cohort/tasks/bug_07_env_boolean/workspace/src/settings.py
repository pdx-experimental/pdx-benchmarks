def run(payload):
    value = payload['value'].strip().lower()
    if value in {'true','yes','1','on'}: return {'value': True}
    if value in {'false','no','0','off'}: return {'value': False}
    return {'value': True}
