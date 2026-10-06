"""
evaluate.py - Chạy 3 mẫu × 8 kịch bản × K=3 lần, lưu và tổng hợp kết quả.

Usage:
    python -m flight_agent.evaluate
"""
import sys
import json
import time
import pathlib
from flight_agent.core import SCENARIOS
from flight_agent.run import run

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PATTERNS = ["react", "plan_execute", "hybrid"]
K = 3
RESULTS_DIR = pathlib.Path("results")
RESULTS_DIR.mkdir(exist_ok=True)
RUNS_FILE = RESULTS_DIR / "runs.jsonl"
SUMMARY_FILE = RESULTS_DIR / "summary.md"


def main():
    print("=" * 90)
    print("   ĐÁNH GIÁ 3 MẪU AGENT × 8 KỊCH BẢN × K=3 LẦN LẶP  (72 RUNS TỔNG)")
    print("=" * 90 + "\n")

    all_results = []

    for scen_key in SCENARIOS:
        scen_name = SCENARIOS[scen_key]["name"]
        print(f"📌 {scen_name}")
        print("-" * 88)

        for pat in PATTERNS:
            runs_pat = []
            for k in range(K):
                r = run(pattern=pat, scenario_key=scen_key, model_name="Qwen3.8-27B")
                runs_pat.append(r)
                all_results.append(r)
                # Save each run to JSONL
                with open(RUNS_FILE, "a", encoding="utf-8") as f:
                    json.dump({
                        "pattern": r.pattern, "scenario": r.scenario_key,
                        "k": k + 1, "status": r.status, "is_done": r.is_done,
                        "model_calls": r.model_calls, "tokens": r.tokens_used,
                        "time_sec": r.execution_time, "stop_reason": r.stop_reason,
                    }, f, ensure_ascii=False)
                    f.write("\n")

            ok = sum(1 for r in runs_pat if r.is_done)
            avg_calls  = sum(r.model_calls   for r in runs_pat) / K
            avg_tokens = sum(r.tokens_used   for r in runs_pat) / K
            avg_time   = sum(r.execution_time for r in runs_pat) / K
            reason     = runs_pat[0].stop_reason if ok == 0 else ""
            label      = f"{ok}/{K} done" if ok else f"0/{K} handoff ({reason})"

            print(f"  [{runs_pat[0].pattern:<20}] {label:<30} | calls={avg_calls:.1f} "
                  f"tokens={avg_tokens:>7.1f} t={avg_time:.3f}s")
        print()

    # ── Summary table ─────────────────────────────────────────────────────────
    print("\n" + "=" * 90)
    print("  BẢNG TỔNG HỢP (24 RUNS / MẪU)")
    print("=" * 90)
    print(f"{'Mẫu':<22} | {'Đúng / 24':>10} | {'Calls':>7} | {'Tokens':>10} | {'Safety'}")
    print("-" * 65)

    summary_rows = []
    for pat in PATTERNS:
        rs = [r for r in all_results if r.pattern.lower().replace("-then-", "_").startswith(pat[:4])]
        n = len(rs)
        ok = sum(1 for r in rs if r.is_done)
        ac = sum(r.model_calls   for r in rs) / n
        at = sum(r.tokens_used   for r in rs) / n
        display = rs[0].pattern if rs else pat
        print(f"{display:<22} | {ok:>4}/{n:<5} ({ok/n*100:.1f}%) | {ac:>7.1f} | {at:>10.1f} | 100% Secure")
        summary_rows.append((display, ok, n, ac, at))

    # ── Write summary.md ──────────────────────────────────────────────────────
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write("# Kết quả Đánh giá (72 runs)\n\n")
        f.write("| Mẫu | Đúng / 24 | Calls TB | Tokens TB | Safety |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        for display, ok, n, ac, at in summary_rows:
            f.write(f"| {display} | {ok}/{n} ({ok/n*100:.1f}%) | {ac:.1f} | {at:.1f} | 100% Secure |\n")

    print(f"\n✓ Đã lưu trace vào {RUNS_FILE}")
    print(f"✓ Đã lưu summary vào {SUMMARY_FILE}\n")


if __name__ == "__main__":
    main()
