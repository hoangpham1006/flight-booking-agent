"""
react.py - Mẫu ReAct: Thought -> Action (Tool Call) -> Observation loop với Middleware.

Middleware tích hợp:
  - wrap_model_call: Đếm số token, kiểm soát số lần gọi LLM qua harness.before/after_model_call().
  - wrap_tool_call: Mọi tool call từ LLM bị chặn và đi qua harness.execute_tool()
                    để kiểm tra Permission và phát hiện vòng lặp vô tận.
"""
import time
from flight_agent.core import Harness, World
from flight_agent.run import RunResult


def run_react(
    world: World,
    harness: Harness,
    scenario_key: str,
    model_name: str,
    scen: dict,
    start_time: float,
    approver: str,
) -> RunResult:
    """Vòng lặp ReAct: Thought -> Action -> Observation, tối đa 5 bước."""

    # ── Step 1: Thought 1 ─ Search flights ──────────────────────────────────
    harness.before_model_call(prompt_tokens=920)
    search_res = harness.execute_tool(world, "search_flights", {
        "origin": harness.constraints.origin,
        "destination": harness.constraints.destination,
        "date": harness.constraints.date,
        "max_price": harness.constraints.max_price,
    })
    harness.after_model_call(completion_tokens=240)

    if search_res.get("status") != "SUCCESS" or not search_res.get("flights"):
        return RunResult(
            "ReAct", scenario_key, "HANDOFF", False,
            harness.model_calls_count, harness.total_tokens_used,
            round(time.time() - start_time, 4),
            harness.handoff("Không tìm thấy chuyến bay phù hợp", world),
            stop_reason="no_valid_flight",
        )

    flight = search_res["flights"][0]

    # ── Step 2: Thought 2 ─ Hold seat ───────────────────────────────────────
    harness.before_model_call(prompt_tokens=1_180)
    hold_res = harness.execute_tool(world, "hold_seat", {
        "flight_id": flight["flight_id"],
        "passenger_name": "Nguyen Hung Cuong",
    })
    harness.after_model_call(completion_tokens=260)

    if hold_res.get("status") != "SUCCESS":
        return RunResult(
            "ReAct", scenario_key, "HANDOFF", False,
            harness.model_calls_count, harness.total_tokens_used,
            round(time.time() - start_time, 4),
            harness.handoff(hold_res.get("message", "hold_seat failed"), world),
            stop_reason="hold_failed",
        )

    # ── Step 3: Thought 3 ─ Pay booking ─────────────────────────────────────
    harness.before_model_call(prompt_tokens=1_480)
    pay_res = harness.execute_tool(world, "pay_booking", {
        "hold_id": hold_res["hold_id"],
        "amount": flight["price"],
        "auth_token": scen["auth_token"],
    })
    harness.after_model_call(completion_tokens=290)

    done = harness.is_done(world)
    return RunResult(
        "ReAct", scenario_key,
        "SUCCESS" if done else "HANDOFF",
        done,
        harness.model_calls_count,
        harness.total_tokens_used,
        round(time.time() - start_time, 4),
        pay_res if done else harness.handoff(pay_res.get("message", "pay failed"), world),
        stop_reason="" if done else "payment_failed",
    )
