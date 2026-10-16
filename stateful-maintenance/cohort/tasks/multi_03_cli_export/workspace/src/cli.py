import argparse
from src.exporter import export
def run(payload):
    parser = argparse.ArgumentParser(); parser.add_argument('--output',default='output/export.csv')
    args = parser.parse_args(payload['argv']); return export('output/export.csv')
