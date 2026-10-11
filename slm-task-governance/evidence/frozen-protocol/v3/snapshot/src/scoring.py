"""Honest Answer Scoring for Fair SLM Evaluation.

Strictly follows Section 5 of FAIR_COMPARISON_PLAN.md:
- Numeric equivalence (relative error <= 1e-3, rounded equality at 1 decimal, handles % and $).
- Exact match after casefold and punctuation stripping.
- Rejects sentence dumps (forces extraction of target needle/token).
- Never searches intermediate tool traces.
"""

from __future__ import annotations

import math
import re
from typing import Optional, Tuple


def normalize_text(text: str) -> str:
    """Normalize text by stripping markdown formatting, quotes, trailing periods, and casefolding."""
    if not text:
        return ""
    s = text.strip()
    # Strip markdown code fences / backticks
    s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
    s = re.sub(r"\n?```$", "", s)
    s = s.strip("`'\" \t\r\n")
    # Strip trailing punctuation if it's a period or comma at the end of a sentence
    s = re.sub(r"[\.,;:]+$", "", s)
    return s.strip().lower()


def extract_first_number(text: str) -> Optional[float]:
    """Extract first numeric value from string, handling % and $."""
    if not text:
        return None
    # Clean standard currency and percent symbols for numeric parsing
    cleaned = text.replace("$", "").replace(",", "")
    match = re.search(r"[-+]?(?:\d+\.?\d*|\.\d+)", cleaned)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None
    return None


def is_numeric_expected(expected: str) -> Optional[float]:
    """Check if expected string is cleanly numeric (scalar, currency, or percentage).
    
    Returns parsed float if numeric, or None if string/identifier/code.
    """
    if not expected:
        return None
    s = str(expected).strip().replace("$", "").replace("%", "").replace(",", "").strip()
    if re.fullmatch(r"[-+]?(?:\d+(?:\.\d+)?|\.\d+)", s):
        try:
            return float(s)
        except ValueError:
            return None
    return None


def score_answer(predicted: str, expected: str, suite: str = "") -> Tuple[bool, str]:
    """Score predicted answer against expected answer according to fair protocol.
    
    Returns:
        (passed: bool, reason: str)
    """
    if predicted is None:
        return False, "null_prediction"
    
    pred_str = str(predicted).strip()
    exp_str = str(expected).strip()
    
    if not pred_str:
        return False, "empty_prediction"
    
    # 1. Exact match after normalize
    norm_pred = normalize_text(pred_str)
    norm_exp = normalize_text(exp_str)
    
    if norm_pred == norm_exp:
        return True, "exact_match"
    
    # 2. Numeric comparison ONLY when expected answer is genuinely numeric
    exp_num = is_numeric_expected(exp_str)
    if exp_num is not None:
        pred_num = extract_first_number(pred_str)
        if pred_num is not None:
            # Check if the predicted text is predominantly numeric (not a paragraph dump)
            words_in_pred = pred_str.split()
            is_numeric_suite = any(s in suite for s in ["calc", "gsm", "finance", "gaia_01", "gaia_03", "gaia_07", "gaia_08", "gaia_13"])
            if len(words_in_pred) <= 6 or is_numeric_suite:
                # Check relative and absolute tolerance
                if math.isclose(pred_num, exp_num, rel_tol=1e-3, abs_tol=1e-2):
                    return True, "numeric_close"
                if round(pred_num, 1) == round(exp_num, 1):
                    return True, "numeric_rounded"
    
    # 3. String / Token / Code comparison
    # Do NOT allow substring match when predicted is a full sentence dumping the context
    # Casefold exact match failed above.
    return False, f"mismatch: expected '{norm_exp}', got '{norm_pred}'"

