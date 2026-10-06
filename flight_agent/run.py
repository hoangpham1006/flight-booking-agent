"""
run.py - Entry point duy nhất: run(pattern, scenario, model, approver) -> RunResult
"""
import time
from dataclasses import dataclass, field
from typing import Any, Optional
from pydantic import ValidationError

from flight_agent.core import SCENARIOS, Constraints, Harness, World


@dataclass
class RunResult:
    pattern: str
    scenario_key: str
    status: str
    is_done: bool
    model_calls: int
    tokens_used: int
    execution_time: float
    details: Any
    stop_reason: str = ""


def run(
    pattern: str,
    scenario_key: str,
    model_name: str = "Qwen3.8-27B",
    approver: str = "auto",
) -> RunResult:
    """Entry point duy nhất thực thi Agent theo mẫu thiết kế chỉ định."""
    from flight_agent import react, plan_execute, hybrid

    scen = SCENARIOS[scenario_key]
    start_time = time.time()

    # ---- Layer 1: Data Constraints Check ----
    if "invalid_raw" in scen:
        try:
            Constraints(**scen["invalid_raw"])
        except ValidationError as e:
            return RunResult(
                pattern=pattern,
                scenario_key=scenario_key,
                status="DATA_CONSTRAINT_ERROR",
                is_done=False,
                model_calls=0,
                tokens_used=0,
                execution_time=round(time.time() - start_time, 4),
                details=str(e),
                stop_reason="data_constraint_violation",
            )

    constraints = scen["constraints"]
    world = World(list(scen["flights"]))
    harness = Harness(constraints, max_budget_user=scen["user_max_budget"])

    # ---- Dispatch to pattern ----
    dispatch = {
        "react": react.run_react,
        "plan_execute": plan_execute.run_plan_execute,
        "hybrid": hybrid.run_hybrid,
    }
    if pattern not in dispatch:
        raise ValueError(f"Pattern '{pattern}' không hợp lệ. Chọn: react | plan_execute | hybrid")

    return dispatch[pattern](world, harness, scenario_key, model_name, scen, start_time, approver)
