"""Recompute exploratory paired statistics from every released task outcome."""
import json
from pathlib import Path
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[1] / "data/results_formal_candidate"


def holm(values):
    out = [0.0] * len(values)
    maximum = 0.0
    for rank, i in enumerate(sorted(range(len(values)), key=lambda i: values[i])):
        maximum = max(maximum, min(1.0, (len(values) - rank) * values[i]))
        out[i] = maximum
    return out


def compare(first, second):
    def load(job):
        rows = [json.loads(line) for line in (ROOT / job / "benchmark_ledger.jsonl").read_text(encoding="utf-8").splitlines()]
        if len({row["task_id"] for row in rows}) != len(rows):
            raise ValueError("Duplicate task")
        return {row["task_id"]: row["success"] for row in rows}
    x, y = load(first), load(second)
    if x.keys() != y.keys():
        raise ValueError("Unpaired task sets")
    a = sum(x[t] and y[t] for t in x)
    b = sum(x[t] and not y[t] for t in x)
    c = sum(not x[t] and y[t] for t in x)
    d = len(x) - a - b - c
    return {"first": first, "second": second, "n": len(x), "a": a, "b": b, "c": c, "d": d,
            "delta": c-b, "p_raw": float(binomtest(b, b+c).pvalue) if b+c else 1.0}


def compute():
    p3 = []
    for model in ("qwen7", "llama8", "apertus", "mistral", "qwen15", "llama3"):
        for first, second in (("c0", "c2sf"), ("c0", "c2s"), ("c2s", "c2sf")):
            p3.append(compare(f"phase3_{model}_{first}", f"phase3_{model}_{second}"))
    for row, value in zip(p3, holm([row["p_raw"] for row in p3])):
        row["holm_m18"] = value
    selected = p3[::3]
    for row, value in zip(selected, holm([row["p_raw"] for row in selected])):
        row["holm_m6_posthoc"] = value
    p0 = [compare(f"phase0_{model}_react", f"phase0_{model}_isolated") for model in
          ("qwen25_15b", "qwen25_3b", "llama32_1b", "llama32_3b", "gemma3_1b")]
    for row, value in zip(p0, holm([row["p_raw"] for row in p0])):
        row["holm_m5"] = value
    without_gemma = p0[:-1]
    sensitivity = [{"first": r["first"], "second": r["second"], "holm_m4_excluding_gemma": v}
                   for r, v in zip(without_gemma, holm([r["p_raw"] for r in without_gemma]))]
    return {"scope": "Exploratory; no confirmatory preregistration claim", "phase3": p3, "phase0": p0,
            "posthoc_sensitivity_excluding_gemma": sensitivity}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
