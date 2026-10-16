"""Symmetric stateful task tools with a real PDX ArtifactRuntime G path.

This adapter applies task policy and JSON Schema before execution. G submits each
operation as a registered PDX execution-plan tool step; R invokes the same narrow
handler directly. It does not claim OS sandboxing or DynamicDispatchService CAS
receipts; those are separate admission requirements.
"""
from __future__ import annotations

import fnmatch
import hashlib
from importlib.metadata import version as package_version
import json
import pathlib
import shutil
import subprocess
import tempfile
import uuid
from typing import Any

from jsonschema import Draft202012Validator
from pdx_artifact_engine import ArtifactRuntime
from pdx_artifact_engine.registry import SkillDefinition, SkillRegistry


TOOL_SCHEMAS: dict[str, tuple[dict, dict]] = {
    "read_file": ({"type":"object","additionalProperties":False,"required":["path"],"properties":{"path":{"type":"string","minLength":1,"maxLength":240},"max_lines":{"type":"integer","minimum":1,"maximum":500}}}, {"type":"object","required":["content"],"properties":{"content":{"type":"string"}},"additionalProperties":False}),
    "list_files": ({"type":"object","additionalProperties":False,"properties":{"directory":{"type":"string","maxLength":240}},"required":[]}, {"type":"object","required":["paths"],"properties":{"paths":{"type":"array","items":{"type":"string"},"maxItems":500}},"additionalProperties":False}),
    "apply_patch": ({"type":"object","additionalProperties":False,"required":["patch_text"],"properties":{"patch_text":{"type":"string","minLength":1,"maxLength":65536}}}, {"type":"object","required":["changed_paths"],"properties":{"changed_paths":{"type":"array","items":{"type":"string"},"maxItems":32}},"additionalProperties":False}),
    "write_file": ({"type":"object","additionalProperties":False,"required":["path","content"],"properties":{"path":{"type":"string","minLength":1,"maxLength":240},"content":{"type":"string","maxLength":65536}}}, {"type":"object","required":["changed_paths"],"properties":{"changed_paths":{"type":"array","items":{"type":"string"}}},"additionalProperties":False}),
    "submit_completion": ({"type":"object","additionalProperties":False,"required":["claimed_success","disposition","summary"],"properties":{"claimed_success":{"type":"boolean"},"disposition":{"type":"string","minLength":1},"summary":{"type":"string"}}}, {"type":"object","required":["accepted","scope"],"properties":{"accepted":{"type":"boolean"},"scope":{"type":"string"}},"additionalProperties":False}),
    "run_visible_tests": ({"type":"object","additionalProperties":False,"required":["target"],"properties":{"target":{"type":"string","enum":["syntax","workspace"]}}}, {"type":"object","required":["exit_code","summary"],"properties":{"exit_code":{"type":"integer"},"summary":{"type":"string","maxLength":2000}},"additionalProperties":False}),
}
UNKNOWN_TOOL_SCHEMA = ({"type":"object","additionalProperties":False,"required":["name"],"properties":{"name":{"type":"string","maxLength":120}}}, {"type":"object","required":["error"],"properties":{"error":{"type":"string","maxLength":500}},"additionalProperties":False})


class StatefulToolAdapter:
    def __init__(self, workspace: pathlib.Path, task_spec: dict, *, arm: str, evidence_dir: pathlib.Path):
        if arm not in {"R", "G"}:
            raise ValueError("arm must be R or G")
        self.workspace = workspace.resolve(strict=True)
        self.task_spec = task_spec
        self.arm = arm
        self.evidence_dir = evidence_dir
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        if not (self.workspace / ".git").exists():
            subprocess.run(["git", "init", "-q"], cwd=self.workspace, check=True, capture_output=True)
            subprocess.run(["git", "-c", "user.name=PDX Fixture", "-c", "user.email=fixture@invalid", "add", "-f", "-A"], cwd=self.workspace, check=True, capture_output=True)
            subprocess.run(["git", "-c", "user.name=PDX Fixture", "-c", "user.email=fixture@invalid", "commit", "-qm", "trusted baseline"], cwd=self.workspace, check=True, capture_output=True)
        self.call_index = 0
        self._last_result: dict[str, Any] = {}
        self._handlers = {name: self._handler(name) for name in (*TOOL_SCHEMAS, "reject_unknown_tool")}
        skills = []
        for name, (ins, outs) in {**TOOL_SCHEMAS, "reject_unknown_tool": UNKNOWN_TOOL_SCHEMA}.items():
            skills.append(SkillDefinition(name=f"pdx.stateful.{name}", version="1.0.0", domain="stateful-maintenance", description=f"Bounded {name} task workspace operation", entrypoint=f"stateful_tool_adapter:{name}", inputs=("arguments",), outputs=("result",), artifacts=("result",), failure_codes=({"code":"TOOL_REJECTED","meaning":"Tool request rejected by task policy or schema"},), verification_hooks=(), input_schema=ins, output_schema=outs))
        self.registry = SkillRegistry(skills)
        self.executors = {f"pdx.stateful.{name}": self._executor(name) for name in (*TOOL_SCHEMAS, "reject_unknown_tool")}
        self.runtime = ArtifactRuntime(self.registry, self.executors, planner_name="stateful-gov")

    def _resolve(self, rel: str) -> pathlib.Path:
        p = pathlib.PurePosixPath(rel)
        if p.is_absolute() or ".." in p.parts or not p.parts or "\\" in rel:
            raise ValueError("path must be a safe workspace-relative path")
        target = self.workspace.joinpath(*p.parts)
        current = self.workspace
        for part in p.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError("symlink paths are not allowed")
        resolved = target.resolve(strict=False)
        if not resolved.is_relative_to(self.workspace):
            raise ValueError("path escapes workspace")
        return target

    def _in_scope(self, rel: str, *, write: bool) -> bool:
        if not write:
            return True
        patterns = self.task_spec["acceptance"].get("allowed_paths", []) if write else ["**/*"]
        return any(fnmatch.fnmatchcase(rel, p) or p.endswith("/**") and (rel == p[:-3] or rel.startswith(p[:-2])) for p in patterns)

    def _handler(self, name: str):
        def call(args: dict[str, Any]) -> dict[str, Any]:
            if 'tool_allowlist' in self.task_spec and name not in self.task_spec['tool_allowlist']:
                raise ValueError(f'tool unavailable in this admission: {name}; use write_file(path, content) for edits')
            if name == "reject_unknown_tool":
                Draft202012Validator(UNKNOWN_TOOL_SCHEMA[0]).validate(args)
                raise ValueError(f"tool is not registered: {args['name']}")
            Draft202012Validator(TOOL_SCHEMAS[name][0]).validate(args)
            if name == "write_file":
                rel = args["path"]
                path = self._resolve(rel)
                if not self._in_scope(rel, write=True):
                    raise ValueError(f"write outside task allowlist: {rel}")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(args["content"], encoding="utf-8")
                return {"changed_paths": [rel]}
            if name == "submit_completion":
                changed = subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=self.workspace, check=True, capture_output=True, text=True).stdout.strip()
                required = self.task_spec["acceptance"].get("required_disposition")
                if required and (args["disposition"] != required or args["claimed_success"] or changed):
                    raise ValueError(f"safe stop requires disposition={required}, claimed_success=false, and no changes")
                if args["claimed_success"]:
                    if not changed:
                        raise ValueError("cannot claim a completed modification: workspace has no changes")
                    check = self._handlers["run_visible_tests"]({"target": "syntax"})
                    if check["exit_code"]:
                        raise ValueError("cannot submit invalid syntax: " + check["summary"])
                return {"accepted": True, "scope": "submission and syntax only; correctness requires external oracle"}
            if name == "read_file":
                rel = args["path"]
                path = self._resolve(rel)
                if not self._in_scope(rel, write=False) or not path.is_file():
                    raise ValueError("file is unavailable")
                lines = path.read_text(encoding="utf-8").splitlines()
                return {"content":"\n".join(lines[:args.get("max_lines", 300)])}
            if name == "list_files":
                rel = args.get("directory", ".")
                root = self.workspace if rel == "." else self._resolve(rel)
                if not root.is_dir():
                    raise ValueError("directory is unavailable")
                paths = sorted(p.relative_to(self.workspace).as_posix() for p in root.rglob("*") if p.is_file() and not p.is_symlink() and '.git' not in p.relative_to(self.workspace).parts)
                return {"paths":paths[:500]}
            if name == "apply_patch":
                patch = args["patch_text"]
                with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".patch", delete=False) as f:
                    f.write(patch)
                    patch_file = pathlib.Path(f.name)
                try:
                    proc = subprocess.run(["git", "-c", "core.autocrlf=false", "apply", "--recount", "--ignore-whitespace", str(patch_file)], cwd=self.workspace, capture_output=True, text=True)
                finally:
                    patch_file.unlink(missing_ok=True)
                if proc.returncode:
                    raise ValueError("patch rejected: " + proc.stderr[-500:])
                status = subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=self.workspace, capture_output=True, text=True, check=True).stdout.splitlines()
                names = [line[3:] for line in status if len(line) >= 4]
                for rel in names:
                    try:
                        self._resolve(rel)
                        in_scope = self._in_scope(rel, write=True)
                    except ValueError:
                        in_scope = False
                    if not in_scope:
                        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=self.workspace, capture_output=True, check=True)
                        subprocess.run(["git", "clean", "-fdx"], cwd=self.workspace, capture_output=True, check=True)
                        raise ValueError(f"write outside task allowlist: {rel}")
                return {"changed_paths":sorted(names)}
            if name == "run_visible_tests":
                errors=[]
                for path in sorted(self.workspace.rglob("*.py")):
                    if path.is_symlink():
                        errors.append(f"symlink:{path.relative_to(self.workspace)}")
                    else:
                        try: compile(path.read_text(encoding="utf-8"), str(path), "exec")
                        except Exception as exc: errors.append(f"python:{path.relative_to(self.workspace)}:{exc}")
                for path in sorted(self.workspace.rglob("*.json")):
                    try: json.loads(path.read_text(encoding="utf-8"))
                    except Exception as exc: errors.append(f"json:{path.relative_to(self.workspace)}:{exc}")
                return {"exit_code":1 if errors else 0,"summary":"; ".join(errors)[:2000] if errors else "Python and JSON syntax checks passed"}
            raise ValueError("unknown tool")
        return call

    def _executor(self, name: str):
        def execute(inputs: dict[str, Any], _out_dir: pathlib.Path) -> dict[str, Any]:
            result = self._handlers[name](inputs["arguments"])
            self._last_result = result
            return {"result": result, "outputs":{"result":result}}
        return execute

    def dispatch(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        self.call_index += 1
        requested_name = name
        requested_arguments = arguments
        if self.arm == "R":
            if name not in TOOL_SCHEMAS:
                requested_name = name
                name = "reject_unknown_tool"
                arguments = {"name": str(requested_name)[:120]}
            result = self._handlers[name](arguments)
            return {"result":result,"governed":False,"engine_evidence":None}
        if name not in TOOL_SCHEMAS:
            name = "reject_unknown_tool"
            arguments = {"name": str(requested_name)[:120]}
        call_id = f"call_{self.call_index:03d}_{uuid.uuid4().hex[:8]}"
        out = self.evidence_dir / call_id
        plan = {"schema_version":"pdx_execution_plan_v1","request_id":call_id,"producer":{"type":"manual","name":"stateful-rg-adapter"},"intent":{"artifact_type":"tool-call","summary":f"Governed {name} invocation"},"steps":[{"id":"dispatch","kind":"tool","tool":f"pdx.stateful.{name}","inputs":{"arguments":arguments},"outputs":["result"],"policies":{"approval_required":False}}],"verification":[{"id":"dispatch_completed","check":"step_completed:dispatch","fail_action":"stop"}],"policies":{"timeout_seconds":30,"max_retries":0,"default_approval_required":False}}
        try:
            result = self.runtime.execute_plan(plan, out)
            manifest = result["run_manifest"]
        except Exception as exc:
            # Engine was invoked; preserve a local adapter record of fail-closed rejection.
            manifest = {"status":"failed","errors":[f"{type(exc).__name__}: {str(exc)[:500]}"]}
            result = {"artifact_manifest":{}}
        record = {"engine":"pdx-artifact-engine","engine_version":package_version("pdx-artifact-engine"),"request_id":call_id,"tool":name,"requested_tool":requested_name,"requested_arguments_sha256":hashlib.sha256(json.dumps(requested_arguments,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"arguments_sha256":hashlib.sha256(json.dumps(arguments,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"run_manifest":manifest,"artifact_manifest":result["artifact_manifest"]}
        record_path = out / "adapter_evidence.json"
        record_path.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        evidence={"path":str(record_path),"sha256":hashlib.sha256(record_path.read_bytes()).hexdigest(),"run_status":manifest["status"]}
        if manifest.get("status") not in {"completed","completed_with_review"}:
            return {"result":{"error":manifest.get("errors") or "PDX tool execution failed"},"governed":True,"engine_evidence":evidence}
        return {"result":self._last_result,"governed":True,"engine_evidence":evidence}
