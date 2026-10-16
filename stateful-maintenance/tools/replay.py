"""Optional Docker Oracle replay of recorded candidates; never run during export verification."""
import argparse,json
from pathlib import Path
from oracle_replay import evaluate
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--version',choices=['v23','v34'],required=True);p.add_argument('--task');args=p.parse_args()
    original=json.loads((ROOT/'runs'/args.version/'host_evaluation.json').read_text(encoding='utf-8'))
    rows=[r for r in original['score_rows'] if not args.task or r['task_id']==args.task]
    if not rows:raise ValueError('Unknown task')
    for r in rows:
        folder=ROOT/'runs'/args.version/(r['task_id']+'_'+r['arm'])
        result=evaluate(r['task_id'],folder/'candidate.patch',json.loads((folder/'completion.json').read_text(encoding='utf-8')))
        print(json.dumps({'task_id':r['task_id'],'arm':r['arm'],'recorded':r['status'],'replayed':result},ensure_ascii=True))
        if result['status']!=r['status']:raise ValueError('Oracle replay differs from recorded status')
if __name__=='__main__':main()
