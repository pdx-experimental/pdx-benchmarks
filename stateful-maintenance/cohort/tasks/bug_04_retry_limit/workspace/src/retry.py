def run(payload):
    n = payload['max_attempts']
    return {'attempts': list(range(1, n + 2)), 'delays': [0] + [payload['delay_seconds']] * (n - 1)}
