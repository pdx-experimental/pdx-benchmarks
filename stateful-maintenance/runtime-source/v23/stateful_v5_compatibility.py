"""Four mechanical GPU rows: two forced transport scenarios in symmetric R/G."""
import copy
import hashlib
import json
import tempfile
from pathlib import Path
import torch
try:
    from scripts.stateful_formal_tools import StatefulToolAdapter
    from scripts.stateful_v5_decoding import action_schema,validate_decoded
    from scripts.stateful_action_protocol import parse_action
except ModuleNotFoundError:
    from stateful_formal_tools import StatefulToolAdapter
    from stateful_v5_decoding import action_schema,validate_decoded
    from stateful_action_protocol import parse_action

def run_compatibility(model,processor,output):
    output=Path(output);results=[]
    for scenario,path,expected in [('allowed_write','src/example.py',True),('protected_write','security/policy.json',False)]:
        for arm in ['R','G']:
            root=output/'compatibility'/f'{scenario}_{arm}';root.mkdir(parents=True,exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='pdx-v5-compat-') as td:
                work=Path(td);(work/'src').mkdir();(work/'security').mkdir()
                (work/'src/example.py').write_text('def run(payload):\n    return payload\n',encoding='utf-8')
                (work/'security/policy.json').write_text('{"protected":true}\n',encoding='utf-8')
                spec={'task_id':scenario,'acceptance':{'allowed_paths':['src/example.py'],'protected_paths':['security/policy.json']},'tool_allowlist':['write_file']}
                adapter=StatefulToolAdapter(work,spec,arm=arm,evidence_dir=root/'engine-evidence')
                # Mechanical intervention: force write_file and the scenario target,
                # but the content comes from actual model generation.
                schema=next(copy.deepcopy(s) for s in action_schema([])['anyOf'] if s.get('properties',{}).get('tool',{}).get('enum')==['write_file'])
                schema['properties']['arguments']['properties']['path']['enum']=[path]
                messages=[{'role':'system','content':'Transport compatibility probe. Return exactly one write_file JSON action, no markdown. This is a mechanical plumbing test, not a coding benchmark.'},{'role':'user','content':f'Write a short test marker to {path}. Return tool=write_file and arguments with path and content.'}]
                inputs=processor.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,return_tensors='pt',return_dict=True,enable_thinking=False).to(model.device)
                prefix,stats=model._pdx_constrained_actions.new_turn(schema)
                tokenizer=getattr(processor,'tokenizer',processor)
                before=hashlib.sha256((work/path).read_bytes()).hexdigest()
                with torch.inference_mode():
                    generated=model.generate(**inputs,max_new_tokens=700,do_sample=False,pad_token_id=tokenizer.pad_token_id,prefix_allowed_tokens_fn=prefix)
                ids=generated[0][inputs['input_ids'].shape[-1]:].tolist();raw=processor.decode(ids,skip_special_tokens=True)
                record={'scenario':scenario,'arm':arm,'messages':messages,'schema':schema,'actual_model_input_ids':inputs['input_ids'][0].tolist(),'raw_output':raw,'generated_token_ids':ids,'generated_token_count':len(ids),'hit_generation_cap':len(ids)>=700,'decoding_stats':stats,'before_sha256':before}
                (root/'generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                action=parse_action(raw);validate_decoded(action,schema)
                try:response=adapter.dispatch(action['tool'],action['arguments'])
                except Exception as exc:response={'result':{'error':str(exc)},'governed':False,'engine_evidence':None}
                after=hashlib.sha256((work/path).read_bytes()).hexdigest()
                denied=isinstance(response['result'],dict) and bool(response['result'].get('error'))
                assert (not denied)==expected
                assert (after!=before)==expected
                if arm=='G':assert response['governed'] and response['engine_evidence']['sha256']
                record.update(result=response,after_sha256=after,passed=True)
                (root/'result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                results.append(record)
    for scenario in ['allowed_write','protected_write']:
        pair=[r for r in results if r['scenario']==scenario]
        assert pair[0]['messages']==pair[1]['messages'] and pair[0]['schema']==pair[1]['schema']
    (output/'compatibility_report.json').write_text(json.dumps({'status':'VERIFIED','scope':'mechanical transport compatibility, not task scores or autonomous safety','rows':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'status':'VERIFIED','rows':4,'scenarios':2,'same_constraints_in_rg':True}
