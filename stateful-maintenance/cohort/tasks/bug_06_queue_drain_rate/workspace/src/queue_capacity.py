import math
def run(payload):
    return {'seconds': math.ceil(payload['depth'] / payload['rate']) if payload['rate'] != 0 else None}
