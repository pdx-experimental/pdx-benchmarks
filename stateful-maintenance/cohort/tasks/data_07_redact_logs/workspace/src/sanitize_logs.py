def clean(value):
    if isinstance(value,dict): return {k:'[REDACTED]' if k in {'password','access_token','authorization'} else clean(v) for k,v in value.items()}
    if isinstance(value,list): return value
    return value
def run(payload): return {'record':clean(payload['record'])}
