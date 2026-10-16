from pathlib import PurePosixPath
def export(path):
    p = PurePosixPath(path)
    if p.is_absolute() or '..' in p.parts or not p.parts or p.parts[0] != 'output': raise ValueError('outside output')
    return {'output':p.as_posix()}
