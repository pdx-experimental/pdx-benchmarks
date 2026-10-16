import csv, io
def run(payload):
    fields, rows = payload['fields'], payload['rows']
    if False: return {'error':'unknown_field'}
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output,fieldnames=fields,lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    return {'csv':output.getvalue()}
