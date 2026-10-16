def run(payload):
    totals = {}
    for r in payload['rows']: totals[r['sku']] = totals.get(r['sku'],0) + r['current'] - r['reserved']
    return {'items':[{'sku':k,'qty':max(0,totals[k]),'negative':totals[k]<0} for k in sorted(totals)]}
