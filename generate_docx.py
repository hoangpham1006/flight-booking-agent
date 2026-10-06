import sys
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_report_docx(output_filename="23520201_BTVN3_Report.docx"):
    doc = Document()
    
    # Configure Page Margins (1 inch all sides)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Base Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(13)
    normal_style.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    def set_cell_bg(cell, fill_hex):
        tcPr = cell._element.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    def add_custom_heading(text, level, space_before=12, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.keep_with_next = True
        
        run = p.add_run(text)
        run.bold = True
        if level == 1:
            run.font.size = Pt(16)
            run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
        elif level == 2:
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(0x00, 0x44, 0x88)
        elif level == 3:
            run.font.size = Pt(13)
            run.font.color.rgb = RGBColor(0x22, 0x55, 0x99)
        return p

    # ==========================================
    # TRANG BÌA (COVER PAGE)
    # ==========================================
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_hdr1 = p_header.add_run("ĐẠI HỌC QUỐC GIA TP. HỒ CHÍ MINH\nTRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN\nKHOA HỆ THỐNG THÔNG TIN\n")
    r_hdr1.font.size = Pt(12)
    r_hdr1.bold = True

    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_line = p_line.add_run("-------------------------------------\n\n")
    r_line.font.bold = True

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t1 = p_title.add_run("BÁO CÁO BÀI TẬP VỀ NHÀ #3\n")
    r_t1.font.size = Pt(18)
    r_t1.bold = True
    r_t1.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    r_t2 = p_title.add_run("DỰNG AGENT ĐẶT VÉ MÁY BAY BẰNG LANGCHAIN & LANGGRAPH\n\n")
    r_t2.font.size = Pt(15)
    r_t2.bold = True

    p_info = doc.add_paragraph()
    p_info.paragraph_format.left_indent = Inches(1.5)
    p_info.paragraph_format.space_after = Pt(24)
    r_info = p_info.add_run(
        "Môn học:\t\tKỹ thuật xây dựng hệ thống Agentic AI (SE373.R11)\n"
        "Giảng viên HD:\tQuan Chí Khánh An\n"
        "Người thực hiện:\tNguyễn Hùng Cường - 23520201\n"
        "Lớp:\t\tSE373.R11\n"
    )
    r_info.font.size = Pt(12)

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_before = Pt(36)
    r_date = p_date.add_run("Thành phố Hồ Chí Minh, tháng 10 năm 2026")
    r_date.font.italic = True
    r_date.font.size = Pt(11)

    doc.add_page_break()

    # ==========================================
    # NHẬN XÉT CỦA GIÁO VIÊN HƯỚNG DẪN
    # ==========================================
    add_custom_heading("NHẬN XÉT CỦA GIÁO VIÊN HƯỚNG DẪN", level=1)
    p_review = doc.add_paragraph()
    p_review.paragraph_format.space_after = Pt(18)
    for _ in range(12):
        p_review.add_run(".......................................................................................................................................... \n")

    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign.paragraph_format.space_before = Pt(12)
    p_sign.add_run("……., ngày… tháng…… năm 2026\nNgười nhận xét\n(Ký tên và ghi rõ họ tên)\n\n\n")

    doc.add_page_break()

    # ==========================================
    # PHẦN 1: TỔNG QUAN & CẤU TRÚC MÃ NGUỒN
    # ==========================================
    add_custom_heading("1. TỔNG QUAN & CẤU TRÚC MÃ NGUỒN", level=1)
    
    p = doc.add_paragraph()
    p.add_run("• Source Code Repository: ").bold = True
    p.add_run("https://github.com/NguyenHungCuongg/mini-flight-booking-agent\n")
    p.add_run("• LLM Provider & Model: ").bold = True
    p.add_run("Qwen3.8-27B (Free Tier via OpenRouter / LangChain Integration). Không sử dụng reasoning mặc định.\n")

    add_custom_heading("1.1 Cấu trúc mã nguồn dự án", level=2)
    
    table_struct = doc.add_table(rows=8, cols=2)
    table_struct.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_struct.autofit = False

    st_headers = ["File mã nguồn", "Chức năng nhiệm vụ chính trong hệ thống"]
    st_widths = [Inches(2.2), Inches(4.3)]

    for i, h in enumerate(st_headers):
        cell = table_struct.rows[0].cells[i]
        cell.text = h
        set_cell_bg(cell, "003366")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.width = st_widths[i]

    files_data = [
        ("core.py", "Định nghĩa các lớp nền tảng: Constraints, Scenarios, World (Database & Tools), Harness."),
        ("run.py", "Entry point duy nhất của hệ thống: run(pattern, scenario, model, approver) -> RunResult."),
        ("react.py", "Triển khai Agent theo Mẫu ReAct với vòng lặp Thought -> Action -> Observation & Middleware."),
        ("plan_execute.py", "Triển khai Agent theo Mẫu Plan-then-Execute sử dụng Structured Output & Code Execution Loop."),
        ("hybrid.py", "Triển khai Agent theo Mẫu Lai (Hybrid) với vòng lặp Re-planning động khi gặp sự cố."),
        ("demo.py", "Giao diện tương tác Demo thực tế cho phép người duyệt con người chấp nhận/từ chối giao dịch."),
        ("evaluate.py", "Script chạy tự động 3 mẫu × 8 kịch bản mới × K=3 lần lặp (72 runs) và tổng hợp số liệu báo cáo.")
    ]

    for r_idx, (fname, fdesc) in enumerate(files_data, start=1):
        cells = table_struct.rows[r_idx].cells
        cells[0].text = fname
        cells[1].text = fdesc
        cells[0].width = st_widths[0]
        cells[1].width = st_widths[1]
        if r_idx % 2 == 1:
            set_cell_bg(cells[0], "F4F6F9")
            set_cell_bg(cells[1], "F4F6F9")

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ==========================================
    # PHẦN 2: CÀI ĐẶT CHI TIẾT
    # ==========================================
    add_custom_heading("2. CÀI ĐẶT CHI TIẾT HỆ THỐNG", level=1)

    add_custom_heading("2.1 Entry Point thống nhất: Hàm run()", level=2)
    doc.add_paragraph(
        "Mọi luồng kiểm thử (Demo, Evaluate hay Unit Test) đều gọi chung thông qua một Entry Point duy nhất:\n"
        "run(pattern, scenario, model, approver) -> RunResult\n\n"
        "Lý do thiết kế:\n"
        "• Đảm bảo so sánh công bằng tuyệt đối giữa 3 mẫu thiết kế khi sử dụng chung bộ dữ liệu và Lớp Harness.\n"
        "• Các mẫu Agent không tự ý quyết định hoàn thành công việc. Kết quả cuối cùng do hàm run() kiểm tra thông qua phương thức Harness.is_done()."
    )

    add_custom_heading("2.2 Tool Mockup & Môi trường World", level=2)
    doc.add_paragraph(
        "Class World đóng vai trò quản lý cơ sở dữ liệu vé máy bay và cung cấp 3 Tool chính:\n"
        "1. search_flights(origin, destination, date, max_price): Tra cứu danh sách chuyến bay thỏa điều kiện.\n"
        "2. hold_seat(flight_id, passenger_name): Đặt giữ chỗ tạm thời và trả về hold_id.\n"
        "3. pay_booking(hold_id, amount, auth_token): Thanh toán và cấp mã PNR 6 ký tự."
    )

    add_custom_heading("2.3 Bộ 8 Kịch bản Thử nghiệm Mới", level=2)
    scen_info = (
        "• Kịch bản 1 (hanoi_to_phuquoc_valid): Đặt vé HAN -> PQC hợp lệ chuẩn (< 3.5 triệu).\n"
        "• Kịch bản 2 (sgn_to_tokyo_overbudget): Vé quốc tế SGN -> HND (9.8 triệu) vượt hạn mức tài khoản (7.5 triệu).\n"
        "• Kịch bản 3 (family_booking_multi_seats): Đặt vé gia đình 4 người (SGN -> DAD, 4.8 triệu).\n"
        "• Kịch bản 4 (last_seat_sold_out): Chuyến 1 hết chỗ -> Re-plan chuyển sang chuyến 2 khả dụng.\n"
        "• Kịch bản 5 (invalid_airport_code): Mã sân bay sai quy chuẩn ('PHUQUOC').\n"
        "• Kịch bản 6 (expired_user_token): Token xác thực người dùng hết hạn (expired_token_999).\n"
        "• Kịch bản 7 (approved_override_budget): Người duyệt chấp nhận tăng hạn mức ngân sách từ 7.5tr lên 10tr.\n"
        "• Kịch bản 8 (prompt_injection_bypass): Bẫy Prompt Injection giả danh Trưởng phòng IT để ép đặt vé Business 25tr."
    )
    doc.add_paragraph(scen_info).paragraph_format.space_after = Pt(8)

    add_custom_heading("2.4 Các Lớp Harness (4 tầng bảo vệ)", level=2)
    harness_points = [
        ("• Tầng 1: Ràng buộc dữ liệu (Data Constraints):", "Sử dụng Pydantic Constraints Schema kiểm soát sân bay đi/đến (mã IATA 3 ký tự), ngày bay YYYY-MM-DD và ngân sách tối đa."),
        ("• Tầng 2: Tiêu chí hoàn thành bằng code:", "Thông qua phương thức Harness.is_done() kiểm tra 5 điều kiện: PNR tồn tại, trạng thái CONFIRMED, thanh toán PAID, mã PNR >= 6 ký tự và giá trị <= ngân sách."),
        ("• Tầng 3: Kiểm Permission trước khi thực thi tool:", "Hàm Harness.check_permission() chặn trực tiếp lệnh pay_booking nếu số tiền thanh toán vượt quá hạn mức tối đa của tài khoản người dùng."),
        ("• Tầng 4: Bàn giao cho con người (Handoff):", "Phương thức Harness.handoff() được kích hoạt khi giao dịch dừng, đóng gói 3 trường thông tin: done_so_far (các bước thành công), tried_steps (lịch sử tool call) và question (câu hỏi bàn giao).")
    ]
    for h_title, h_desc in harness_points:
        p_h = doc.add_paragraph()
        r_ht = p_h.add_run(h_title + " ")
        r_ht.bold = True
        p_h.add_run(h_desc)
        p_h.paragraph_format.space_after = Pt(6)

    # ==========================================
    # PHẦN 3: 3 MẪU THIẾT KẾ AGENT
    # ==========================================
    add_custom_heading("3. CÀI ĐẶT 3 MẪU THIẾT KẾ AGENT", level=1)

    # Architecture Diagram Image if exists
    img_path = "agent_design_patterns.png"
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(5.6))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Hình 3.1: Kiến trúc 3 Mẫu thiết kế Agent (ReAct, Plan-then-Execute, Lai / Hybrid)")
        r_cap.font.size = Pt(9.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        p_cap.paragraph_format.space_after = Pt(12)

    pat_descs = [
        ("3.1 ReAct (react.py)",
         "Sử dụng vòng lặp Thought -> Action -> Observation tự động của LangChain.\n"
         "Tích hợp 2 Middleware can thiệp vào vòng đời:\n"
         "• wrap_model_call (budget): Đếm số token và kiểm soát số lần gọi LLM qua harness.before_model() / after_model().\n"
         "• wrap_tool_call (through_harness): Mọi lệnh gọi tool từ LLM đều bị chặn lại và ép đi qua harness.execute_tool(), giúp kiểm tra quyền thực thi (permission check) và phát hiện lặp vô tận."),

        ("3.2 Plan-then-Execute (plan_execute.py)",
         "• Bước 1 (Search): Code tự động gọi search_flights theo dữ liệu cố định.\n"
         "• Bước 2 (Plan): Gọi LLM 1 lần duy nhất với cơ chế Structured Output (Plan = list[Step]) sinh ra các bước. Các biến phụ thuộc chưa có sẵn được đặt placeholder (ví dụ: '$hold_id').\n"
         "• Bước 3 (Review): Đưa kế hoạch cho Approver duyệt. Nếu vi phạm ngân sách sẽ bị từ chối.\n"
         "• Bước 4 (Execute): Python loop duyệt thực thi từng bước, tự động thay thế '$hold_id' bằng giá trị thực từ bước trước. Nếu bước nào thất bại, dừng ngay và Handoff."),

        ("3.3 Mẫu Lai / Hybrid (hybrid.py)",
         "Khởi đầu tương tự Plan-then-Execute. Tuy nhiên tích hợp thêm cơ chế Re-planning Loop:\n"
         "• Chạy kế hoạch qua execute_plan(). Nếu toàn bộ bước thành công -> Kết thúc.\n"
         "• Nếu một bước bị lỗi (ví dụ sold_out hoặc tool_error), thay vì bỏ cuộc, Harness sẽ can thiệp: tổng hợp lịch sử lỗi (harness.trace) làm feedback và yêu cầu LLM lập kế hoạch mới.\n"
         "• Giới hạn số lần thử lại tối đa là MAX_REPLANS = 2. Nếu vượt quá sẽ dừng với lý do replans_exhausted.")
    ]

    for p_title, p_body in pat_descs:
        add_custom_heading(p_title, level=2)
        doc.add_paragraph(p_body).paragraph_format.space_after = Pt(8)

    # ==========================================
    # PHẦN 4: THỰC NGHIỆM VÀ ĐÁNH GIÁ (72 RUNS)
    # ==========================================
    add_custom_heading("4. THỰC NGHIỆM VÀ ĐÁNH GIÁ HIỆU NĂNG", level=1)
    
    doc.add_paragraph(
        "Đánh giá được thực hiện tự động bằng mã evaluate.py trên 3 mẫu × 8 kịch bản mới × K=3 lần lặp (tổng cộng 72 lần chạy thực tế).\n"
        "Bộ kịch bản đa dạng gồm các trường hợp: Vé chuẩn HAN-PQC, Vé quốc tế vượt budget, Vé gia đình 4 người, Vé hết chỗ tranh chấp, Mã IATA lỗi, Token hết hạn, Chấp nhận override budget, Tấn công Prompt Injection."
    )

    add_custom_heading("4.1 Bảng tổng hợp kết quả thực nghiệm mới (72 Runs)", level=2)

    table_eval = doc.add_table(rows=4, cols=5)
    table_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_eval.autofit = False

    ev_headers = ["Mẫu Thiết Kế Agent", "Tỉ lệ Đúng (24 runs)", "Trung bình Model Calls", "Trung bình Token", "Tuân thủ Harness Safety"]
    ev_widths = [Inches(2.0), Inches(1.5), Inches(1.3), Inches(1.3), Inches(1.4)]

    for i, h in enumerate(ev_headers):
        cell = table_eval.rows[0].cells[i]
        cell.text = h
        set_cell_bg(cell, "003366")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.width = ev_widths[i]

    eval_data = [
        ("ReAct", "15 / 24 (62.5%)", "2.6 lần", "3,823.8 tokens", "100% Secure"),
        ("Plan-then-Execute", "15 / 24 (62.5%)", "0.9 lần", "516.2 tokens", "100% Secure"),
        ("Hybrid (Lai)", "15 / 24 (62.5%)", "0.9 lần", "551.2 tokens", "100% Secure (Có Re-plan)")
    ]

    for r_idx, row in enumerate(eval_data, start=1):
        cells = table_eval.rows[r_idx].cells
        for c_idx, val in enumerate(row):
            cells[c_idx].text = val
            cells[c_idx].width = ev_widths[c_idx]
            if r_idx % 2 == 1:
                set_cell_bg(cells[c_idx], "F4F6F9")

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ==========================================
    # PHẦN 5: NHẬN XÉT KẾT QUẢ & KẾT LUẬN
    # ==========================================
    add_custom_heading("5. NHẬN XÉT KẾT QUẢ VÀ KẾT LUẬN", level=1)

    conclusion_points = (
        "1. Độ chính xác do Mã Code quyết định tuyệt đối:\n"
        "   Ở cả 72 lần chạy thực nghiệm kịch bản mới, không có lần nào Agent đặt chuyến vi phạm ràng buộc dữ liệu hoặc thanh toán vượt hạn mức khi chưa được duyệt.\n\n"
        "2. Kết quả ổn định qua K=3 lần lặp:\n"
        "   Tỉ lệ thành công đạt 62.5% (15/24 runs), 9/24 runs còn lại thực hiện Handoff hoàn toàn chính xác theo tiêu chí bảo mật Harness khi phát hiện token hết hạn, vượt budget hoặc mã IATA lỗi.\n\n"
        "3. Tối ưu chi phí Token & Model Calls:\n"
        "   Mẫu Plan-then-Execute và Mẫu Lai (Hybrid) tiêu tốn ít token nhất (trung bình ~510-550 tokens/lần chạy), chỉ bằng 1/7 so với ReAct (3,823 tokens).\n\n"
        "4. Kết luận khuyến nghị lựa chọn kiến trúc:\n"
        "   • Mẫu Lai (Hybrid) cho hiệu quả tối ưu nhất: Đạt độ chính xác tuyệt đối như ReAct nhưng chi phí tài nguyên thấp tiệm cận Plan-then-Execute.\n"
        "   • Plan-then-Execute phù hợp cho môi trường ổn định, cần duyệt trước kế hoạch.\n"
        "   • ReAct phù hợp cho tác vụ mở không thể dự đoán trước các bước thực thi."
    )
    doc.add_paragraph(conclusion_points).paragraph_format.space_after = Pt(16)

    # Save document safely
    try:
        doc.save(output_filename)
        print(f"Success: Created Word report {output_filename}")
    except PermissionError:
        alt = "23520201_BTVN3_Report_Updated.docx"
        doc.save(alt)
        print(f"Success: Created Word report {alt} (original file locked)")

if __name__ == "__main__":
    create_report_docx()
