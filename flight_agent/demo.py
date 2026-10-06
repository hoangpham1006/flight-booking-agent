"""
demo.py - Demo tương tác: người duyệt là người thật.

Usage:
    python -m flight_agent.demo
"""
import sys
from flight_agent.core import SCENARIOS
from flight_agent.run import run

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PATTERNS = ["react", "plan_execute", "hybrid"]


def choose(options: list, prompt: str) -> str:
    print(f"\n{prompt}")
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    while True:
        try:
            idx = int(input("Chọn số: ")) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except (ValueError, KeyboardInterrupt):
            pass
        print("  Vui lòng nhập số hợp lệ.")


def main():
    print("=" * 60)
    print("  DEMO AGENT ĐẶT VÉ MÁY BAY - SE373.R11 BTVN#3")
    print("=" * 60)

    pat  = choose(PATTERNS, "Chọn mẫu thiết kế:")
    scen = choose(list(SCENARIOS.keys()), "Chọn kịch bản:")

    print(f"\n▶ Chạy [{pat}] với [{scen}] ...\n")
    result = run(pattern=pat, scenario_key=scen, approver="human_interactive")

    print("\n" + "─" * 60)
    print(f"  Trạng thái   : {result.status}")
    print(f"  Hoàn thành   : {result.is_done}")
    print(f"  Lý do dừng   : {result.stop_reason or 'N/A'}")
    print(f"  Model calls  : {result.model_calls}")
    print(f"  Tokens dùng  : {result.tokens_used}")
    print(f"  Thời gian    : {result.execution_time:.4f}s")
    if result.is_done and isinstance(result.details, dict):
        print(f"  PNR          : {result.details.get('pnr', 'N/A')}")
    print("─" * 60 + "\n")


if __name__ == "__main__":
    main()
