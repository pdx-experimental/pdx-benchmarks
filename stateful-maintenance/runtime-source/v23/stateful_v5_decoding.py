"""Symmetric token-time JSON constraints; never repairs or salvages generated text."""
import copy
import hashlib
import json
import sys
from pathlib import Path
from importlib.metadata import version
from jsonschema import Draft202012Validator
try:
    from scripts.stateful_tool_adapter import TOOL_SCHEMAS
except ModuleNotFoundError:
    from stateful_tool_adapter import TOOL_SCHEMAS

BACKEND_VERSION='0.11.3'
LOCAL_DEPS=Path(__file__).resolve().parents[1]/'artifacts/stateful-formal-v5/python-deps'
if LOCAL_DEPS.exists():sys.path.insert(0,str(LOCAL_DEPS))

def action_schema(dispositions):
    branches=[]
    for name in ['read_file','list_files','write_file','run_visible_tests']:
        arguments=copy.deepcopy(TOOL_SCHEMAS[name][0])
        if name=='read_file':arguments['properties']['max_lines']['enum']=list(range(1,501))
        if name=='run_visible_tests':arguments['properties']['target']['enum']=['syntax']
        branches.append({'type':'object','additionalProperties':False,'required':['tool','arguments'],'properties':{'tool':{'type':'string','enum':[name]},'arguments':arguments}})
    branches.append({'type':'object','additionalProperties':False,'required':['action','claimed_success','disposition','summary'],'properties':{'action':{'type':'string','enum':['final']},'claimed_success':{'type':'boolean'},'disposition':{'type':'string','enum':sorted(set(dispositions)|{'COMPLETED','UNVERIFIED_INCOMPLETE'})},'summary':{'type':'string','minLength':1}}})
    return {'anyOf':branches}

def validate_decoded(action,schema):
    Draft202012Validator(schema).validate(action)

def compile_parser(schema,config=None):
    from lmformatenforcer import JsonSchemaParser
    return JsonSchemaParser(schema,config=config)

def to_dispatch_action(action,schema):
    validate_decoded(action,schema)
    if action.get('action')=='final':
        return {'final':True,'claimed_success':action['claimed_success'],'disposition':action['disposition'],'summary':action['summary']}
    return copy.deepcopy(action)

class ConstrainedActions:
    def __init__(self,tokenizer,vocab_size):
        assert version('lm-format-enforcer')==BACKEND_VERSION
        from lmformatenforcer import TokenEnforcerTokenizerData
        self.vocab_size=int(vocab_size)
        assert 0<self.vocab_size<=len(tokenizer)
        # Use the public backend API: its 0.11.3 HF helper imports a symbol removed
        # in Transformers 5. This adapter does not patch that wheel or downgrade HF.
        zero=tokenizer.encode('0',add_special_tokens=False)[-1]
        assert tokenizer.decode([zero])=='0'
        native=getattr(tokenizer,'backend_tokenizer',None)
        if native is None:raise RuntimeError('Validated integration requires the pinned fast tokenizer')
        decode_native=lambda ids:native.decode(ids,skip_special_tokens=False)
        # Fast native decoding avoids the Python HF wrapper for every vocab item.
        # Verify equivalence before constructing the complete output token tree.
        for token in [0,zero,self.vocab_size//2,self.vocab_size-1]:
            assert decode_native([zero,token])==tokenizer.decode([zero,token],clean_up_tokenization_spaces=False)
        special=set(tokenizer.all_special_ids);regular=[]
        for token in range(self.vocab_size):
            if token in special:continue
            raw=decode_native([token])
            following=decode_native([zero,token])[1:]
            regular.append((token,following,len(following)>len(raw)))
        decode=lambda ids:decode_native(ids).rstrip('\ufffd')
        self.tokenizer_data=TokenEnforcerTokenizerData(regular,decode,tokenizer.eos_token_id,False,self.vocab_size)
        self.tokenizer=tokenizer

    def new_turn(self,schema):
        from lmformatenforcer import TokenEnforcer,CharacterLevelParserConfig
        config=CharacterLevelParserConfig(alphabet=self.tokenizer_data.tokenizer_alphabet)
        enforcer=TokenEnforcer(self.tokenizer_data,compile_parser(schema,config=config))
        stats={'backend':'lm-format-enforcer','version':BACKEND_VERSION,'output_vocab_size':self.vocab_size,'schema_sha256':hashlib.sha256(json.dumps(schema,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'mask_calls':0}
        def guarded(batch_id,input_ids):
            allowed=enforcer.get_allowed_tokens(input_ids.tolist()).allowed_tokens
            if not allowed or any(type(t) is not int or t<0 or t>=self.vocab_size for t in allowed):
                raise RuntimeError('Invalid/empty constrained token set; no unconstrained fallback')
            stats['mask_calls']+=1
            return allowed
        return guarded,stats

def output_vocab_size(model):
    layer=model.get_output_embeddings()
    if layer is None or not hasattr(layer,'weight'):raise RuntimeError('Cannot establish actual output-head vocabulary')
    return int(layer.weight.shape[0])
