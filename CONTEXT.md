# CONTEXT

## Bài toán
Dựng Agent đặt vé máy bay bằng LangChain / LangGraph — BTVN#3, môn **SE373.R11 Kỹ thuật xây dựng hệ thống Agentic AI**, ĐHCNTT - ĐHQG TP.HCM.

## Ràng buộc chung cho mọi kịch bản
- Ngày khởi hành: `2026-11-10` hoặc `2026-11-15`
- Ngân sách người dùng Standard: tối đa **3.500.000 VNĐ / giao dịch**
- Mã sân bay đầu vào: đúng chuẩn **IATA 3 ký tự in hoa** (ví dụ: `HAN`, `PQC`, `SGN`)
- Auth token: phải hợp lệ, không bắt đầu bằng `expired`

## Thiết kế Harness (4 tầng)
1. **Data Constraints** — Pydantic schema chặn trước khi Agent xử lý.
2. **Programmatic Done Check** — `Harness.is_done()` kiểm 5 điều kiện bằng code.
3. **Permission Check** — `Harness.check_permission()` chặn `pay_booking` nếu vượt budget.
4. **Handoff** — `Harness.handoff()` đóng gói `done_so_far`, `tried`, `question`.

## Cơ chế dừng bổ sung
- ReAct: dừng sau tối đa 5 bước Thought-Action-Observation.
- Plan-then-Execute: dừng nếu bất kỳ bước nào trong plan fail.
- Hybrid: dừng nếu vượt `MAX_REPLANS = 2`.

## Model
Qwen3.8-27B (Free Tier, OpenRouter). Temperature = 0. Reasoning off.
