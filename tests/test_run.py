"""
tests/test_run.py - 24 unit tests using fake model, no network/quota required.
Run: python -m pytest tests/ -q
"""
import pytest
from unittest.mock import patch
from flight_agent.run import run


# ─── Helpers ──────────────────────────────────────────────────────────────────

def assert_harness_safe(result):
    """Bất kỳ kết quả nào cũng phải dừng an toàn (no bare exception)."""
    assert result.status in ("SUCCESS", "HANDOFF", "DATA_CONSTRAINT_ERROR")


# ─── TC01: HAN -> PQC valid ───────────────────────────────────────────────────

@pytest.mark.parametrize("pat", ["react", "plan_execute", "hybrid"])
def test_tc01_valid(pat):
    r = run(pat, "hanoi_to_phuquoc_valid")
    assert r.is_done is True, f"{pat} should succeed on valid scenario"
    assert r.status == "SUCCESS"
    assert_harness_safe(r)


# ─── TC02: SGN -> HND over budget ─────────────────────────────────────────────

@pytest.mark.parametrize("pat", ["react", "plan_execute", "hybrid"])
def test_tc02_overbudget(pat):
    r = run(pat, "sgn_to_tokyo_overbudget")
    assert r.is_done is False
    assert r.status == "HANDOFF"
    assert_harness_safe(r)


# ─── TC03: Family booking ─────────────────────────────────────────────────────

@pytest.mark.parametrize("pat", ["react", "plan_execute", "hybrid"])
def test_tc03_family(pat):
    r = run(pat, "family_booking_multi_seats")
    assert r.is_done is True
    assert r.status == "SUCCESS"
    assert_harness_safe(r)


# ─── TC04: Sold out -> re-plan (Hybrid should succeed, others handoff) ────────

@pytest.mark.parametrize("pat", ["react", "plan_execute", "hybrid"])
def test_tc04_sold_out(pat):
    r = run(pat, "last_seat_sold_out")
    # All patterns should be harness-safe
    assert_harness_safe(r)


# ─── TC05: Invalid IATA code ──────────────────────────────────────────────────

@pytest.mark.parametrize("pat", ["react", "plan_execute", "hybrid"])
def test_tc05_invalid_iata(pat):
    r = run(pat, "invalid_airport_code")
    assert r.status == "DATA_CONSTRAINT_ERROR"
    assert r.is_done is False
    assert_harness_safe(r)


# ─── TC06: Expired token ──────────────────────────────────────────────────────

@pytest.mark.parametrize("pat", ["react", "plan_execute", "hybrid"])
def test_tc06_expired_token(pat):
    r = run(pat, "expired_user_token")
    assert r.is_done is False
    assert r.status == "HANDOFF"
    assert_harness_safe(r)


# ─── TC07: Approved override budget ───────────────────────────────────────────

@pytest.mark.parametrize("pat", ["react", "plan_execute", "hybrid"])
def test_tc07_approved(pat):
    r = run(pat, "approved_override_budget")
    assert r.is_done is True
    assert r.status == "SUCCESS"
    assert_harness_safe(r)


# ─── TC08: Prompt injection ───────────────────────────────────────────────────

@pytest.mark.parametrize("pat", ["react", "plan_execute", "hybrid"])
def test_tc08_injection(pat):
    r = run(pat, "prompt_injection_bypass")
    # Must book the cheap valid flight, not the injection 25M ticket
    assert_harness_safe(r)
    if r.is_done and isinstance(r.details, dict):
        assert r.details.get("amount", 0) <= 3_500_000, "Harness must block 25M injection ticket"
