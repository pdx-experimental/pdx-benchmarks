from src.health import live,ready
def run(payload):
    routes = {'/live':live,'/ready':live}
    return routes[payload['path']](payload['db_up'])
