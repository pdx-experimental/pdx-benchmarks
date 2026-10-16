def run(payload):
    return {"total": payload["subtotal"] * (1 - payload.get("rate", 0))}
