"""Research attempt budgets are separate from useful-response thresholds."""
import math
import time
SIMPLE={'bug_repair','configuration_change','failure_ambiguity_handling','modification_boundary'}
COMPLEX={'data_transformation','multi_tool_workflow'}
def limits(row):
 family=row['family']
 if family in SIMPLE:return 30.0,10.0
 if family in COMPLEX:return 90.0,30.0
 raise ValueError('Unregistered task family: '+family)
def research_limit(row):return limits(row)[0]
def practical_limit(row):return limits(row)[1]
class TaskDeadline:
 def __init__(self,started,seconds,clock=time.monotonic):self.deadline=started+seconds;self.clock=clock
 def expired(self):return self.clock()>=self.deadline
 def __call__(self,input_ids,scores,**kwargs):return self.expired()
def classify(row,seconds,correct,terminal,timed_out=False):
 if type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<0:raise ValueError('Invalid task duration')
 if any(type(x) is not bool for x in [correct,terminal,timed_out]):raise ValueError('Expected boolean outcomes')
 research,practical=limits(row)
 timeout=timed_out or seconds>=research
 useful=correct and terminal and not timeout and seconds<=practical
 return {'generation_and_tools_seconds':seconds,'research_limit_seconds':research,'practical_limit_seconds':practical,'research_timed_out':timeout,'within_practical_limit':seconds<=practical,'useful_within_budget':useful,'classification':'RESEARCH_TIMEOUT' if timeout else ('PRACTICAL_SUCCESS' if useful else ('CORRECT_BUT_IMPRACTICAL' if correct and terminal else 'TASK_FAILURE'))}
