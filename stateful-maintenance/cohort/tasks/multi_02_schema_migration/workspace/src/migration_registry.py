import sqlite3
from src.migrations.event_index import apply
def run(payload):
    db = sqlite3.connect(':memory:'); db.execute('CREATE TABLE events(timestamp TEXT)')
    for _ in range(2): apply(db)
    names = sorted(r[1] for r in db.execute('PRAGMA index_list(events)'))
    db.close(); return {'indexes':names,'order':['base']}
