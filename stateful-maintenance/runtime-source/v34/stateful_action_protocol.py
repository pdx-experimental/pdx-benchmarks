"""Strict, single-action JSON protocol; never infer or salvage partial actions."""
import json

def _pairs(items):
    value={}
    for key,item in items:
        if key in value: raise ValueError('Duplicate JSON key: '+key)
        value[key]=item
    return value

def _constant(value):
    raise ValueError('Non-finite JSON number is forbidden: '+value)

def parse_action(text):
    obj=json.loads(text,object_pairs_hook=_pairs,parse_constant=_constant)
    if not isinstance(obj,dict): raise ValueError('Response must be exactly one JSON action object')
    return obj

def action_protocol_error(action):
    if not isinstance(action,dict): return 'Action must be an object.'
    if 'tool' in action and any(k in action for k in ['final','claimed_success','disposition','summary']):
        return 'Choose one action: tool+arguments OR final completion. Wait for each tool result before the next action.'
    if action.get('final') is True:
        if set(action)!={'final','claimed_success','disposition','summary'}: return 'Terminal response permits only final, claimed_success, disposition, summary.'
        if type(action['claimed_success']) is not bool or not isinstance(action['disposition'],str) or not action['disposition'].strip() or not isinstance(action['summary'],str) or not action['summary'].strip(): return 'Terminal fields require boolean claimed_success and non-empty disposition/summary strings.'
        return None
    if set(action)!={'tool','arguments'}: return 'Tool action must contain only tool and arguments. To finish use final=true in a separate terminal object.'
    if not isinstance(action['tool'],str) or not action['tool'].strip(): return 'Tool name must be a non-empty string.'
    if not isinstance(action['arguments'],dict): return 'Tool arguments must be an object.'
    return None
