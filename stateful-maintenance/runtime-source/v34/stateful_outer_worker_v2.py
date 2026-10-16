"""Keep notebook kernel alive to finalize evidence after a bounded worker exits."""
import json,os,subprocess,time
from pathlib import Path
import psutil

def run_bounded(command,cwd,output,seconds=600):
 output=Path(output);output.mkdir(parents=True,exist_ok=True)
 start=time.monotonic();status={'status':'starting','limit_seconds':seconds}
 def save():
  (output/'outer_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
 save()
 with (output/'whole_execution.log').open('w',encoding='utf-8') as log:
  child=subprocess.Popen(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,start_new_session=(os.name!='nt'))
  status.update(status='running',pid=child.pid);save()
  try:
   code=child.wait(timeout=seconds);status.update(status='completed' if code==0 else 'child_failed',returncode=code)
  except subprocess.TimeoutExpired:
   status.update(status='WHOLE_JOB_TIME_LIMIT',returncode=124);save()
   try:
    descendants=psutil.Process(child.pid).children(recursive=True)
   except psutil.NoSuchProcess:
    descendants=[]
   for descendant in reversed(descendants):
    try:descendant.kill()
    except psutil.NoSuchProcess:pass
   psutil.wait_procs(descendants,timeout=2)
   if os.name!='nt':
    import signal
    try:os.killpg(child.pid,signal.SIGKILL)
    except ProcessLookupError:pass
   else:
    try:
     target=psutil.Process(child.pid)
     for proc in reversed(target.children(recursive=True)):
      try:proc.kill()
      except psutil.NoSuchProcess:pass
     target.kill()
    except psutil.NoSuchProcess:pass
   child.wait(timeout=5)
  finally:
   status['elapsed_seconds']=time.monotonic()-start;save()
 return status
