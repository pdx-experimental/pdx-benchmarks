"""Formal-v3 policy extension; R/G share handler restrictions for host safety."""
import fnmatch
try:
    from scripts.stateful_tool_adapter import StatefulToolAdapter as BaseAdapter
except ModuleNotFoundError:
    from stateful_tool_adapter import StatefulToolAdapter as BaseAdapter

class StatefulToolAdapter(BaseAdapter):
    def _in_scope(self,rel,*,write):
        patterns=self.task_spec['acceptance'].get('protected_paths',[]) if write else self.task_spec.get('forbidden_read_paths',[])
        if any(rel==p or fnmatch.fnmatchcase(rel,p) or p.endswith('/') and rel.startswith(p) for p in patterns): return False
        return super()._in_scope(rel,write=write)
