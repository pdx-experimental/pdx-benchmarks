def run(payload):
    quantity = payload['quantity']
    return {'total': quantity * payload['unit_price'] * (1 + payload['tax_rate']) if quantity else 1}
