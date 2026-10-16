"""External process watchdog: 30s/90s research limits; 10s/30s practical thresholds; fail fast."""
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
from types import SimpleNamespace

PREFIX = 'PDX_PROGRESS '
SIMPLE_SECONDS = 30.0
COMPLEX_SECONDS = 90.0
COLD_START_SECONDS = 300.0


def task_limit(row):
    # Fixed before this performance probe; no model-output-based assignment.
    family = row['family']
    if family in {'data_transformation', 'multi_tool_workflow'}:
        return COMPLEX_SECONDS
    if family in {'bug_repair', 'configuration_change', 'failure_ambiguity_handling', 'modification_boundary'}:
        return SIMPLE_SECONDS
    raise ValueError('Unregistered task family: ' + str(family))


def progress(event, **values):
    print(PREFIX + json.dumps({'event': event, **values}, sort_keys=True), flush=True)


class LiveTrace(list):
    """Persist each event before the next generation; never wait for row completion."""
    def __init__(self, path):
        super().__init__()
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event):
        super().append(event)
        with self.path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + '\n')
            stream.flush()


class ProgressGuard:
    def __init__(self):
        self.epoch = 0
        self.seen = set()

    def repeated(self, action):
        key = (self.epoch, json.dumps(action, sort_keys=True, separators=(',', ':')))
        if key in self.seen:
            return True
        self.seen.add(key)
        return False

    def observe(self, name, result):
        changed = result.get('changed_paths')
        if name in {'write_file','replace_text'} and changed == []:
            return 'NO_EFFECTIVE_CHANGE'
        if changed:
            self.epoch += 1
        return None


def run_supervised(command, *, cwd, output_dir, cold_start_seconds=COLD_START_SECONDS,
                   _test_limits=None):
    """Kill the child independently of its Python/GPU callbacks on deadline.

    Private test limits permit subsecond real-process counterexamples; notebooks
    always use the fixed public 10/30-second contract.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    child = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, encoding='utf-8',
                             errors='replace', bufsize=1)
    lines = queue.Queue(maxsize=1000)
    def consume():
        try:
            for line in iter(lambda: child.stdout.readline(16384), ''):
                lines.put((time.monotonic(), line))
        finally:
            lines.put((time.monotonic(), None))
    reader = threading.Thread(target=consume, daemon=True)
    reader.start()
    deadline = started + cold_start_seconds
    active = None
    report = {'schema': 'pdx.performance-supervisor.v1', 'events': [],
              'status': 'running', 'simple_seconds': SIMPLE_SECONDS,
              'complex_seconds': COMPLEX_SECONDS, 'practical_simple_seconds':10.0,'practical_complex_seconds':30.0,'row_timings': []}
    def save():
        temporary = output_dir / 'supervisor_report.json.tmp'
        temporary.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        temporary.replace(output_dir / 'supervisor_report.json')
    def terminate(reason):
        report.update(status=reason, active_row=active,
                      elapsed_seconds=time.monotonic()-started)
        report['termination_status']='requested'
        save() # Persist the deadline BEFORE any possibly failing process operation.
        try:
            child.kill()
            child.wait(timeout=5)
            report['termination_status']='exited'
        except Exception as exc:
            report['termination_status']='failed'
            report['termination_error']=f'{type(exc).__name__}: {exc}'
        save()
        print(PREFIX+json.dumps({'event':'bounded_trial_stop','reason':reason,'active_row':active}),flush=True)
        return SimpleNamespace(returncode=124, performance_failure=True)
    save()
    log_bytes = 0
    try:
        with (output_dir/'live_execution.log').open('w', encoding='utf-8') as log:
            while True:
                # Check external wall time even if the child keeps printing.
                if time.monotonic() >= deadline:
                    return terminate('TASK_TIME_LIMIT' if active else ('INTER_ROW_TIME_LIMIT' if report['row_timings'] else 'COLD_START_TIME_LIMIT'))
                try:
                    received_at, line = lines.get(timeout=min(0.05, max(0.001, deadline-time.monotonic())))
                except queue.Empty:
                    if child.poll() is not None:
                        break
                    continue
                if line is None:
                    break
                if log_bytes < 1024*1024:
                    log.write(line); log.flush(); log_bytes += len(line.encode('utf-8'))
                if not line.startswith(PREFIX):
                    continue
                event = json.loads(line[len(PREFIX):])
                event['supervisor_received_monotonic'] = received_at
                report['events'].append(event)
                if event['event'] == 'row_start':
                    if active is not None:
                        raise ValueError('Overlapping row_start events')
                    limit = task_limit(event)
                    if _test_limits is not None:
                        limit = _test_limits[event['family']]
                    active = event
                    deadline = float(event.get("started_monotonic", received_at)) + limit + (0 if _test_limits is not None else 2.0) # cancellation/export grace, never scoring time
                elif event['event'] == 'row_end':
                    if active is None or (event['task_id'],event['arm']) != (active['task_id'],active['arm']):
                        raise ValueError('row_end does not match active task')
                    measured = received_at - float(active.get('started_monotonic', received_at))
                    report['row_timings'].append({'task_id':event['task_id'],'arm':event['arm'],'elapsed_seconds':measured,'budget_seconds':task_limit(active),'within_budget':measured<=task_limit(active)})
                    active = None
                    deadline = received_at + min(5.0, cold_start_seconds)
                print(line.rstrip(), flush=True)
                save()
            code = child.wait(timeout=10)
            report.update(status='completed' if code == 0 else 'child_failed',
                          returncode=code, elapsed_seconds=time.monotonic()-started)
            save()
            return SimpleNamespace(returncode=code, performance_failure=False)
    finally:
        if child.poll() is None:
            try:
                child.kill(); child.wait(timeout=5)
            except Exception as exc:
                report['cleanup_error']=f'{type(exc).__name__}: {exc}'
                save()
