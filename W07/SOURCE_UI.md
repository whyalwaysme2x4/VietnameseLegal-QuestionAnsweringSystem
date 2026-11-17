# Source UI — implementation và cách kiểm chứng

| File tại gốc repo | Bằng chứng |
|---|---|
| `app.js::renderSources` | Thẻ nguồn, nhãn NGUỒN ĐƯỢC DẪN/ỨNG VIÊN TRUY XUẤT, nút đọc nguồn |
| `app.js::openSource` | GET /api/source/{id}, mở dialog nội dung, metadata, source_file |
| `app.py::Handler.do_GET` | API đọc nguồn từ Engine, không phải crawler URL web |
| `index.html` | Source dialog và container các thẻ nguồn |
| `source/agent/demo_agentic.py` | Ánh xạ citation agent 0-based sang sources, giữ retrieved_sources riêng |

UI thông báo “Hiệu lực nguồn chưa xác minh”. Xem nguồn không phải xác nhận nguồn còn hiệu lực. Một nguồn có thể là text node Điều/Khoản, không phải toàn DOCX.

## Evidence

- `test-results.json`: kiểm tra contract tĩnh của JS/HTML/API, không phải screenshot.
- `http-contract-smoke.json`: chạy lại smoke HTTP/SSE hiện có với hai ca fixture cho citation 0/1, đọc nội dung đúng và trace finish. Không inference/AWS.
- `figures/citation_refusal_flow.mmd`: sơ đồ luồng đọc code, không phải ảnh runtime.

## Checklist cần ghi hình sau

- [ ] Chạy demo đầy đủ và chụp câu trả lời có nguồn, mở dialog xem nội dung.
- [ ] Chụp một câu ngoài phạm vi và một câu thiếu căn cứ với model thật.
- [ ] Kiểm tra ứng viên không bị hiển thị thành nguồn đã dẫn khi generation lỗi.
- [ ] Kiểm tra tiếng Việt, bố cục và thao tác đóng/mở dialog trên trình duyệt.

Chưa đánh dấu hoàn tất các bước trên chỉ từ code hoặc fixture. Code runtime giữ nguyên; không thêm feature UI mới trong gói W7.
