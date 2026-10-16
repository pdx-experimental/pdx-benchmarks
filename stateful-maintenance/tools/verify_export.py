"""Offline recorded-result verification. No candidate execution or cloud access."""
import hashlib,json,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def require(ok,reason):
    if not ok:raise ValueError(reason)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    inventory=json.loads((ROOT/'PUBLIC_SHA256.json').read_text(encoding='utf-8'))
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p.name!='PUBLIC_SHA256.json' and '__pycache__' not in p.parts}
    require(actual==set(inventory),'export file-set mismatch')
    for rel,digest in inventory.items():require(sha(ROOT/rel)==digest,'hash mismatch: '+rel)
    registry=[json.loads(s) for s in (ROOT/'cohort/registry.jsonl').read_text(encoding='utf-8').splitlines()]
    require(len(registry)==48 and len({r['task_id'] for r in registry})==48,'registry cardinality')
    keys={(r['task_id'],a) for r in registry for a in ['R','G']}
    results={}
    for version in ['v23','v34']:
        base=ROOT/'runs'/version
        evaluation=json.loads((base/'host_evaluation.json').read_text(encoding='utf-8'))
        rows=evaluation['score_rows'];require(len(rows)==96 and {(r['task_id'],r['arm']) for r in rows}==keys,'result bijection')
        counts=collections.Counter();engine=collections.Counter();seen=set()
        for row in rows:
            arm=row['arm'];prefix=base/(row['task_id']+'_'+arm)
            submission=json.loads((prefix/'submission.json').read_text(encoding='utf-8'))
            require(sha(prefix/'candidate.patch')==submission['patch_sha256'],'patch binding')
            counts[arm]+=row['status']=='PASS'
            for event in map(json.loads,(prefix/'trajectory.jsonl').read_text(encoding='utf-8').splitlines()):
                if 'tool' not in event:continue
                if arm=='R':require(not event.get('governed') and not event.get('engine_evidence'),'R governance contamination')
                else:
                    require(event.get('governed') is True,'G ungoverned tool event')
                    evidence=event['engine_evidence'];raw=evidence['path'].replace('\\','/')
                    marker='engine-evidence/'
                    require(marker in raw,'unknown evidence path')
                    rel=marker+raw.split(marker,1)[1]
                    require('..' not in Path(rel).parts,'unsafe evidence reference')
                    require(rel not in seen,'duplicate evidence reference');seen.add(rel)
                    require(sha(base/rel)==evidence['sha256'],'Engine event evidence binding')
                    engine['total']+=1
                    engine['errors']+=bool(event.get('error') or isinstance(event.get('result'),dict) and event['result'].get('error'))
        results[version]={'oracle':dict(counts),'engine_events':dict(engine)}
        if version=='v34':
            for arm in ['R','G']:
                subset=[r for r in rows if r['arm']==arm]
                full=sum(r['status']=='PASS' and r['practicality']['classification'] in ['PRACTICAL_SUCCESS','CORRECT_BUT_IMPRACTICAL'] for r in subset)
                practical=sum(r['practicality']['useful_within_budget'] for r in subset)
                require((counts[arm],full,practical)==(20,16,3),'V34 nested counts')
            require(engine['total']==178 and engine['errors']==12,'V34 Engine counts')
    require(results['v23']['oracle']=={'G':23,'R':23} or results['v23']['oracle']=={'R':23,'G':23},'V23 counts')
    a={};b={}
    for version,target in [('v23',a),('v34',b)]:
        evaluation=json.loads((ROOT/'runs'/version/'host_evaluation.json').read_text(encoding='utf-8'))
        for row in evaluation['score_rows']:
            folder=ROOT/'runs'/version/(row['task_id']+'_'+row['arm'])
            events=list(map(json.loads,(folder/'trajectory.jsonl').read_text(encoding='utf-8').splitlines()))
            first=next(e for e in events if e.get('event')=='actual_model_input')
            target[(row['task_id'],row['arm'])]=(row,folder,first)
    identical=0;losses=[]
    for key in keys:
        x,xf,xi=a[key];y,yf,yi=b[key]
        require(xi['messages']==yi['messages'] and xi['input_token_ids']==yi['input_token_ids'],'initial input mismatch')
        same=(xf/'candidate.patch').read_bytes()==(yf/'candidate.patch').read_bytes()
        identical+=same
        if key[0].startswith(('data_','multi_')):
            require(same,'data/multi patch mismatch')
            require(not y['practicality']['research_timed_out'],'unexpected data/multi deadline')
        if x['status']=='PASS' and y['status']!='PASS':losses.append(key)
        require(not (x['status']!='PASS' and y['status']=='PASS'),'unexpected gain')
    require(identical==92 and len(losses)==6,'paired change accounting')
    print(json.dumps({'status':'VERIFIED','scope':'export integrity, patch/Engine event bindings and recorded score accounting; not inference, independent timestamp or Oracle validity','results':results},indent=2))
if __name__=='__main__':main()
