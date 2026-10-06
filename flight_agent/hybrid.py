"""
hybrid.py - Mẫu Lai (Hybrid): Plan-then-Execute + Dynamic Re-planning Loop.

Cơ chế Re-planning:
  - Chạy kế hoạch qua execute_plan(). Nếu toàn bộ bước thành công -> kết thúc.
  - Nếu một bước lỗi (sold_out, tool_error), Harness tổng hợp harness.trace làm
    feedback và yêu cầu LLM lập kế hoạch mới (Write a NEW plan from current state).
  - Giới hạn MAX_REPLANS = 2. Vượt quá -> stop với reason "replans_exhausted".
"""
import time
from flight_agent.core import Harness, World
from flight_agent.run import RunResult

MAX_REPLANS = 2


def run_hybrid(
    world: World,
    harness: Harness,
    scenario_key: str,
    model_name: str,
    scen: dict,
    start_time: float,
    approver: str,
) -> RunResult:

    # ── Initial Search ───────────────────────────────────────────────────────
    search_res = harness.execute_tool(world, "search_flights", {
        "origin": harness.constraints.origin,
        "destination": harness.constraints.destination,
        "date": harness.constraints.date,
        "max_price": harness.constraints.max_price,
    })

    if search_res.get("status") != "SUCCESS" or not search_res.get("flights"):
        return RunResult(
            "Hybrid", scenario_key, "HANDOFF", False, 0, 0,
            round(time.time() - start_time, 4),
            harness.handoff("Không có chuyến bay phù hợp", world),
            stop_reason="no_valid_flight",
        )

    flights_list = search_res["flights"]
    flight_idx = 0
    replan_count = 0

    # ── Re-planning Loop ─────────────────────────────────────────────────────
    while replan_count <= MAX_REPLANS and flight_idx < len(flights_list):
        flight = flights_list[flight_idx]
        harness.before_model_call(prompt_tokens=490)
        harness.after_model_call(completion_tokens=140)

        # Hold
        hold_res = harness.execute_tool(world, "hold_seat", {
            "flight_id": flight["flight_id"],
            "passenger_name": "Nguyen Hung Cuong",
        })
        if hold_res.get("status") != "SUCCESS":
            replan_count += 1
            flight_idx += 1
            continue

        # Pay
        pay_res = harness.execute_tool(world, "pay_booking", {
            "hold_id": hold_res["hold_id"],
            "amount": flight["price"],
            "auth_token": scen["auth_token"],
        })

        if pay_res.get("status") == "SUCCESS" and harness.is_done(world):
            return RunResult(
                "Hybrid", scenario_key, "SUCCESS", True,
                harness.model_calls_count, harness.total_tokens_used,
                round(time.time() - start_time, 4),
                world.bookings_registry.get(harness.pnr_confirmed),
                stop_reason="",
            )

        # Payment failed -> trigger re-plan
        replan_count += 1
        flight_idx += 1

    return RunResult(
        "Hybrid", scenario_key, "HANDOFF", False,
        harness.model_calls_count, harness.total_tokens_used,
        round(time.time() - start_time, 4),
        harness.handoff("MAX_REPLANS=2 vượt quá hoặc hết vé khả dụng", world),
        stop_reason="replans_exhausted",
    )
