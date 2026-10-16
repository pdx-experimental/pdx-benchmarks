def run(payload):
    selected = {}
    for r in payload['events']:
        key = r['event_id']
        if key not in selected or (r['updated_at'],r['source_priority']) < (selected[key]['updated_at'],selected[key]['source_priority']): selected[key] = r
    return {'events':list(selected.values())}
