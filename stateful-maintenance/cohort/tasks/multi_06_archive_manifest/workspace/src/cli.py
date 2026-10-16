from src.manifest import generate
def run(payload): return generate(payload['files'],payload['output_archive'])
