def run(payload):
    rows = sorted(payload['records'], key=lambda r: r['created_at'])
    return {'ids': [r['record_id'] for r in rows[payload['offset']:payload['offset'] + payload['limit']]]}
