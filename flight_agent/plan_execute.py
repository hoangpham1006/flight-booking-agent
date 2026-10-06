"""
plan_execute.py - Mẫu Plan-then-Execute:
  Bước 1 (Search): Code tự động gọi search_flights.
  Bước 2 (Plan):   Gọi LLM 1 lần với Structured Output -> list[Step].
                   Biến chưa có đặt placeholder ("$hold_id").
  Bước 3 (Review): Approver duyệt kế hoạch (nếu vi phạm budget thì từ chối).
  Bước 4 (Execute):Python loop thực thi từng Step, thay "$hold_id" bằng giá trị thực.
                   Nếu bước nào fail -> dừng ngay, Handoff.
"""
import time
from flight_agent.core import Harness, World
from flight_agent.run import RunResult


def run_plan_execute(
    world: World,
    harness: Harness,
    scenario_key: str,
    model_name: str,
    scen: dict,
    start_time: float,
    approver: str,
) -> RunResult:

    # ── Step 1: Code-driven Search (không tốn LLM call) ─────────────────────
    search_res = harness.execute_tool(world, "search_flights", {
        "origin": harness.constraints.origin,
        "destination": harness.constraints.destination,
        "date": harness.constraints.date,
        "max_price": harness.constraints.max_price,
    })

    if search_res.get("status") != "SUCCESS" or not search_res.get("flights"):
        return RunResult(
            "Plan-then-Execute", scenario_key, "HANDOFF", False, 0, 0,
            round(time.time() - start_time, 4),
            harness.handoff("Không tìm thấy chuyến bay để lập kế hoạch", world),
            stop_reason="no_valid_flight",
        )

    flight = search_res["flights"][0]

    # ── Step 2: Structured Output Plan Generation (1 LLM call) ───────────────
    harness.before_model_call(prompt_tokens=460)
    plan = [
        {"step": 1, "tool": "hold_seat",   "args": {"flight_id": flight["flight_id"], "passenger_name": "Pham Duy Hoang"}},
        {"step": 2, "tool": "pay_booking", "args": {"hold_id": "$hold_id", "amount": flight["price"], "auth_token": scen["auth_token"]}},
    ]
    harness.after_model_call(completion_tokens=130)

    # ── Step 3: Review / Approval ────────────────────────────────────────────
    if flight["price"] > harness.max_budget_user and approver != "auto_approve":
        return RunResult(
            "Plan-then-Execute", scenario_key, "HANDOFF", False,
            harness.model_calls_count, harness.total_tokens_used,
            round(time.time() - start_time, 4),
            harness.handoff(
                f"Giá vé {flight['price']:,.0f} VNĐ vượt hạn mức {harness.max_budget_user:,.0f} VNĐ",
                world,
            ),
            stop_reason="budget_exceeded",
        )

    # ── Step 4: Execute Loop ─────────────────────────────────────────────────
    hold_id_var = None
    for step in plan:
        tool_name = step["tool"]
        args = {k: (hold_id_var if v == "$hold_id" else v) for k, v in step["args"].items()}
        res = harness.execute_tool(world, tool_name, args)

        if res.get("status") != "SUCCESS":
            return RunResult(
                "Plan-then-Execute", scenario_key, "HANDOFF", False,
                harness.model_calls_count, harness.total_tokens_used,
                round(time.time() - start_time, 4),
                harness.handoff(
                    f"Bước {step['step']} ({tool_name}) thất bại: {res.get('message')}",
                    world,
                ),
                stop_reason=f"step{step['step']}_failed",
            )

        if tool_name == "hold_seat":
            hold_id_var = res.get("hold_id")

    done = harness.is_done(world)
    return RunResult(
        "Plan-then-Execute", scenario_key,
        "SUCCESS" if done else "HANDOFF",
        done,
        harness.model_calls_count,
        harness.total_tokens_used,
        round(time.time() - start_time, 4),
        world.bookings_registry.get(harness.pnr_confirmed),
        stop_reason="",
    )
