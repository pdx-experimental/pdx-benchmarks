"""Unit tests for honest answer scoring (Section 5 & Section 9 of FAIR_COMPARISON_PLAN.md)."""

import pytest
from src.scoring import score_answer, normalize_text


def test_scoring_percent_and_numeric():
    # Case 6 requirement: "30.0" vs "30%" -> pass
    passed, reason = score_answer("30.0", "30%", suite="gaia_l1")
    assert passed is True, f"Failed: {reason}"

    # Rounded float
    passed, reason = score_answer("18.40", "18.4%", suite="gaia_l2")
    assert passed is True, f"Failed: {reason}"

    # Currency matching
    passed, reason = score_answer("14.20", "$14.20", suite="gaia_l2")
    assert passed is True, f"Failed: {reason}"


def test_scoring_sentence_dump_rejected():
    # Case 6 requirement: whole needle line dump vs extracted token -> must FAIL
    sentence_dump = "server node-melbourne-4 token is TRN2-SECRET-MEL-9921."
    expected_needle = "TRN2-SECRET-MEL-9921"
    passed, reason = score_answer(sentence_dump, expected_needle, suite="ruler_l1")
    assert passed is False, "Sentence dump without extraction must fail!"


def test_scoring_exact_and_normalized():
    # Exact match with casing / quotes
    passed, _ = score_answer("'Ada Lovelace'", "Ada Lovelace", suite="gaia_l1")
    assert passed is True

    # Code token
    passed, _ = score_answer("`dict.get`", "dict.get", suite="swe_l1")
    assert passed is True

    # Empty / None
    passed, _ = score_answer("", "expected", suite="default")
    assert passed is False
    passed, _ = score_answer(None, "expected", suite="default")
    assert passed is False


def test_scoring_arn_and_string_false_positive_rejected():
    # Crucial regression test: ARN with us-east-1 must NOT match another ARN with us-east-1 via numeric '-1'
    pred_arn = "arn:aws:kms:us-east-1:123456789:key/12345678-1234-1234-1234-123456789012"
    exp_arn = "arn:aws:kms:us-east-1:123456789:key/9918a"
    passed, reason = score_answer(pred_arn, exp_arn, suite="ruler_multihop")
    assert passed is False, f"False positive ARN match must be rejected: {reason}"

    # Number alone should not match string key=val
    passed, reason = score_answer("3", "max_retries=3", suite="swe_l1")
    assert passed is False, f"Number alone must not match key=val: {reason}"

    # City with extra suffix
    passed, reason = score_answer("ap-southeast-4 (Melbourne)", "ap-southeast-4", suite="ruler_l1")
    assert passed is False, f"City with extra explanation must fail exact match: {reason}"

    # True ARN exact match must still succeed
    passed, reason = score_answer("arn:aws:kms:us-east-1:123456789:key/9918a", exp_arn, suite="ruler_multihop")
    assert passed is True, f"Exact ARN match must succeed: {reason}"

