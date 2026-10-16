"""Model-facing observations only. Raw R/G trace and Engine evidence stay intact."""
import re

def normalize_error(error):
    parts=error if isinstance(error,list) else [error]
    text='; '.join(str(p) for p in parts)
    text=re.sub(r'^Step dispatch failed:\s*','',text)
    text=re.sub(r'^(?:ValueError|RuntimeError|ValidationError):\s*','',text)
    if 'write outside task allowlist:' in text:
        return {'code':'WRITE_OUTSIDE_ALLOWLIST','message':text[text.index('write outside task allowlist:'):]}
    if 'file is unavailable' in text:return {'code':'FILE_UNAVAILABLE','message':'file is unavailable'}
    if 'safe stop requires disposition=' in text:
        return {'code':'SAFE_STOP_CONTRACT','message':text[text.index('safe stop requires disposition='):]}
    if 'cannot claim a completed modification:' in text:
        return {'code':'NO_MODIFICATION','message':'cannot claim a completed modification: workspace has no changes'}
    if 'cannot submit invalid syntax:' in text:return {'code':'INVALID_SYNTAX','message':text[text.index('cannot submit invalid syntax:'):]}
    return {'code':'TOOL_ERROR','message':text}

def model_observation(event):
    result=event.get('result',{'error':event.get('error','unknown tool error')})
    if isinstance(result,dict) and 'error' in result:
        return {'tool':event['tool'],'status':'error','error':normalize_error(result['error'])}
    return {'tool':event['tool'],'status':'ok','result':result}

def completion_feedback(result):
    return model_observation({'tool':'submit_completion',**result})
