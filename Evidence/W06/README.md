# W06 — Agent graph Planner/Grader/Checker

Thời gian tuần: **01/11–07/11/2026**. Cập nhật/đóng gói: **05/11/2026**. Code và toàn bộ W01–W06 nằm trên `main`; snapshot W6 là tag `w06`. [Milestone Tuan6](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/6), [thực hiện #17](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/17), [review #18](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/18).

## Kết quả đã có

- Planner giới hạn Giao thông vận tải và Lao động tiền lương, 53 văn bản.
- LangGraph: Planner → multi-query Dense → RRF → CrossEncoder → BERT → Grader → chọn vòng tốt nhất → Generator → Checker → final/regenerate. Giữ tổng hai vòng retrieval, fail-open và key citation 0-based theo nguồn.
- 15/15 test cases đối chiếu luồng agent với Orchestrator tham chiếu, không có failures/errors. [Danh sách case](agent-cases.json), [kết quả](test-results.json), [trace](traces/), [metrics](metrics.csv).
- [Smoke assets](asset-smoke.json): index 6.883 chunks/53 văn bản, nạp BERT thật và một extraction; nạp CrossEncoder mặc định gốc, chưa chạy prediction CE.
- [HTTP/SSE smoke](http-contract-smoke.json): fixture kiểm tra nguồn 0/1, bỏ chỉ số ngoài danh sách, source card và trace đến finish.
- [Migration verification](migration-verification.json): dữ liệu/minh chứng baseline được bảo toàn. [Packaging](packaging.json) ghi hash nguồn và thay đổi đường dẫn khi đưa vào repo. [Manifest](manifest.json) khóa các artifact và code hiện hành bằng SHA-256.

## Phân loại bằng chứng

15 case dùng agent/graph thật nhưng **LLM, retrieval và BERT tensor là fixture**. Pass rate 100% là tỷ lệ đạt kiểm thử luồng, không phải accuracy của model hoặc độ đúng pháp lý. Trace có `fixture_execution=true`, không phải demo AWS thật. [Hình graph](figures/agent-graph.svg) là sơ đồ kiến trúc, không phải ảnh đo runtime.

Chưa chạy toàn bộ agent với AWS thật, chưa đo latency/chất lượng model W6. Không sử dụng điểm W3–W5 làm kết quả W6. Snapshot pháp lý 01/07/2026 và nhãn QA vẫn pending kiểm chứng. Các chính sách fail-open gốc không bảo đảm câu trả lời đúng luật.

## File triển khai và chạy lại

- [Graph](../../source/agent/graph_orchestrator.py), [composition](../../source/agent/demo_agentic.py), [scope](../../source/core/corpus_scope.json).
- [Planner](../../source/agent/planner.py), [Grader](../../source/agent/grader.py), [Checker](../../source/agent/hallucination_checker.py), [BERT](../../source/model/extract_model.py).
- [Hướng dẫn W6](../../W6_IMPLEMENTATION.md), [nguồn tái sử dụng](../../ATTRIBUTION.md).

```powershell
python Evidence/tools/validate_evidence.py
python Evidence/tools/validate_w06.py
.\.venv\Scripts\python.exe -B tests/run_w6_tests.py
```

Hai validator không inference/gọi AWS. Test runner ghi kết quả mới vào `runs/w6/`, không ghi đè evidence. Muốn chạy demo dùng `Start-Demo.ps1` và chọn W6; cần model và cấu hình AWS riêng.

## Review

Tăng Minh Quang (`whyalwaysme2x4`) thực hiện; Đỗ Văn Đức (`dovanduc2004`) được giao review ở issue #18, **chưa có review W6 xác nhận**. W6 không tạo PR theo yêu cầu cập nhật trực tiếp main; không dùng issue này để giả lập minh chứng PR có approval.
