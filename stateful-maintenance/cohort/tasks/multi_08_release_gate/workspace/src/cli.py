from src.release_gate import compatible
def run(payload):
    ok = compatible(payload['min_schema'],payload['max_schema'],payload['deployed'])
    return {'release':payload['tests_passed'] and ok,'compatibility':ok}
