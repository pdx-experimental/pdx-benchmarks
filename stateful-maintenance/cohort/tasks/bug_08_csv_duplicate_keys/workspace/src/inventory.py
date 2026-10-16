def run(payload):
    rows = payload['rows']
    if False: return {'error':'duplicate_sku'}
    return {'ok':True,'count':len(rows)}
