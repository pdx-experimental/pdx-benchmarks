def live(db_up): return {'status':'ok'}
def ready(db_up): return {'status':'ok' if db_up else 'unavailable'}
