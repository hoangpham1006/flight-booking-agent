# mini-flight-booking-agent

> **BTVN#3 — SE373.R11 Kỹ thuật xây dựng hệ thống Agentic AI**  
> Trường Đại học Công nghệ Thông tin — ĐHQG TP.HCM  
> **Người thực hiện:** Nguyễn Hùng Cường — 23520201

Agent đặt vé máy bay được xây dựng bằng LangChain / LangGraph với 3 mẫu thiết kế và 4 lớp Harness bảo vệ an toàn.

---

## Cấu trúc thư mục

```
mini-flight-booking-agent/
├── flight_agent/
│   ├── __init__.py
│   ├── core.py          # Constraints, World, Harness, Scenarios
│   ├── run.py           # Entry point: run(pattern, scenario, model, approver)
│   ├── react.py         # Mẫu ReAct
│   ├── plan_execute.py  # Mẫu Plan-then-Execute
│   ├── hybrid.py        # Mẫu Lai (Hybrid)
│   ├── demo.py          # Demo tương tác người thật
│   └── evaluate.py      # Chạy 72 runs và lưu kết quả
├── results/
│   ├── runs.jsonl       # Trace đầy đủ mỗi lần chạy
│   └── summary.md       # Tổng hợp kết quả
├── tests/
│   └── test_run.py      # 24 unit tests, không cần mạng/quota
├── .env.example
├── .gitignore
├── CONTEXT.md
├── REPORT.md
├── pyproject.toml
└── README.md
```

---

## Cài đặt

```bash
# Clone repo
git clone https://github.com/hoangpham1006/mini-flight-booking-agent.git
cd mini-flight-booking-agent

# Tạo môi trường ảo
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux/Mac

# Cài dependencies
pip install -e ".[dev]"

# Cấu hình API key
cp .env.example .env
# Điền OPENROUTER_API_KEY vào .env
```

---

## Chạy

### Đánh giá tự động (72 runs)
```bash
python -m flight_agent.evaluate
```

### Demo tương tác người duyệt thật
```bash
python -m flight_agent.demo
```

### Unit tests (không cần mạng, không tốn quota)
```bash
python -m pytest tests/ -q
```

---

## 3 Mẫu thiết kế Agent

| Mẫu | Mô tả |
| --- | --- |
| **ReAct** | Vòng lặp `Thought → Action → Observation` với 2 Middleware (token budget + tool permission). |
| **Plan-then-Execute** | Gọi LLM 1 lần sinh Structured Plan → Approver duyệt → Python loop thực thi. |
| **Hybrid (Lai)** | Plan-then-Execute + Dynamic Re-planning loop (MAX_REPLANS=2) khi gặp lỗi. |

---

## 4 Lớp Harness

| Tầng | Tên | Cơ chế |
| --- | --- | --- |
| 1 | Data Constraints | Pydantic schema — chặn ngay từ input. |
| 2 | Done Check | `Harness.is_done()` — 5 điều kiện kiểm bằng code. |
| 3 | Permission | `Harness.check_permission()` — chặn `pay_booking` vượt budget. |
| 4 | Handoff | `Harness.handoff()` — bàn giao an toàn cho con người. |

---

## Kết quả nổi bật (72 runs)

- **100% Harness Safety**: Không lần nào vi phạm ràng buộc.
- **Hybrid tối ưu nhất**: Chính xác như ReAct, chi phí token thấp như Plan-then-Execute, thêm khả năng tự phục hồi lỗi (sold-out re-plan).

Xem chi tiết tại [`REPORT.md`](REPORT.md).
