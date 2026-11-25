# W08 — SSE frontend + history / Integrated app

Tuần kế hoạch **15/11–21/11/2026**. Triển khai, kiểm tra và xuất bản thực tế **25/11/2026**; không backdate. Tất cả trên main, snapshot w08; review theo [github.json](github.json).

## Chức năng và code

- [App/API](../../app.py), [UI](../../app.js), [SSE parser](../../sse.js): sự kiện tiến trình theo bước, heartbeat, UTF-8/frame split và lỗi stream; chưa phải stream token LLM.
- [SQLite history](../../source/data/db/demo_history.py): tạo/chọn/xóa phiên, lưu cặp hỏi–đáp và nguồn/trace nguyên payload, khôi phục sau reload; phân biệt processing/complete/failed.
- [Agent bridge](../../source/agent/demo_agentic.py): ngữ cảnh 5 message gần nhất của đúng phiên; không global facts/LLM summary. Baseline W3–W5 giữ truy vấn độc lập.
- Worker lưu kết quả dù browser disconnect; dừng theo dõi không hủy model phía server. Lỗi DB có cảnh báo riêng, lỗi provider không tạo đáp án giả.
- DB riêng ở local_data, không commit. Không login/per-user ownership; đây là ứng dụng một người dùng chạy loopback.

## Kết quả thực đo bằng fixture

| Kiểm tra | Kết quả | Evidence |
|---|---|---|
| Python integration/regression | 46/46 đạt: 20 W8 + 15 agent + 11 synthesis baseline | [test-results.json](test-results.json) |
| Parser SSE | 8/8 đạt | [test-results-js.json](test-results-js.json) |
| Chrome UI | 8/8 đạt, không JS page errors | [browser-results.json](browser-results.json), [ảnh](figures/) |
| Synthetic history roundtrips | 36/36 đúng, 12 hội thoại/72 tin nhắn | [conversations](synthetic_conversations.json), [logs](synthetic_chat_logs.jsonl) |

6 hội thoại giao thông và 6 lao động, mỗi cuộc 3 lượt. Câu đầu tái sử dụng QA dev có source_qa_id; câu theo sau được viết cho tương tác. Reply/source fixture có nhãn rõ, không phải legal gold hoặc independent test. Không có chat người dùng thật.

## Tái lập và lineage

```powershell
python Evidence/tools/validate_w08.py
node tests/test_sse_w8.cjs
python verify_week_folders.py
.\.venv\Scripts\python.exe -B tests/run_w8_tests.py
```

Validator chỉ đọc; runner dùng DB tạm và ghi runs/w8, không ghi đè evidence. Browser test theo [hướng dẫn](../../W8_IMPLEMENTATION.md). [Manifest](manifest.json) khóa runtime hiện hành và evidence; [packaging](packaging.json) ghi thay đổi đường dẫn evaluation khi xuất bản. [Local snapshot](local_snapshot/README.md) giữ báo cáo trước đóng gói nguyên bytes. [Snapshot lịch sử](../_history/README.md) giữ code/input cũ cho manifest W01–W07, không sửa số liệu/trace/manifest cũ.

[W08 code/data](../../W08/README.md) là bản phân loại để đọc, không phải app độc lập. Chạy app từ gốc repo bằng Start-Demo.ps1. Model weights, index, credentials, DB/log thật và backups không được push.

**Giới hạn:** các model/retrieval dùng fixture trong kiểm thử; không gọi AWS, không đo legal accuracy hoặc latency end-to-end thật. Giữ nguyên kỹ thuật và policy agent, citation 0-based agent/1-based baseline. Review Đức đang chờ; cập nhật trực tiếp main không tạo approval PR giả.
