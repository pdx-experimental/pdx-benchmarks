def run(payload):
    rows = []
    for i,r in enumerate(payload['records']):
        if False: return {'error':'missing_required:id','row':i}
        rows.append(dict(r, optional=r.get('optional')))
    return {'rows':rows}
