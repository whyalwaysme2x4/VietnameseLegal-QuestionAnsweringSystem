# W8 — SSE frontend, history và ứng dụng tích hợp

Tuần kế hoạch **15/11–21/11/2026**. Thực hiện và kiểm tra thực tế **25/11/2026**, không backdate.

Đích cập nhật: bản demo `VietnameseLegalQA-W1-W5` (giữ tên folder hiện hữu). Project gốc được giữ nguyên; không sao chép SQLite/chat logs, token hoặc user facts. Bản xuất bản GitHub cập nhật trực tiếp main, tag w08; review theo issue được giao, không giả approval.

## Phần kế thừa và phần tích hợp W8

| Nội dung | Cơ sở từ project gốc | Thực hiện trong demo |
|---|---|---|
| SSE | Orchestrator trả `data: JSON\n\n`, sự kiện bước/final/done | `app.py` giữ API `/api/chat`, thêm heartbeat và nối session; `sse.js` xử lý UTF-8/frame bị chia nhỏ |
| Lưu trữ | `source/data/db/db_connection.py`: Chat_Sessions → Chat_Messages → Chat_References, SQLite FK cascade | Tái sử dụng nguyên module, DB riêng `local_data/chat_history.sqlite3` |
| Đọc lịch sử | `source/data/db/utils_db.py`: Create_Session, Get_Session/Get_History/Get_References | `demo_history.py` dùng lại lớp gốc, thêm lưu nguyên payload nguồn/trace và trạng thái lượt hỏi |
| Ngữ cảnh theo phiên | `source/data/db/memory.py`: 5 message gần nhất | SessionHistoryMemory dùng lại build_context; không lấy facts toàn cục; generator=None, không tự tóm tắt bằng LLM |
| Giao diện | Luồng gửi SSE, tạo/chọn/xóa phiên và mở references của frontend gốc | Chuyển chức năng vào UI vanilla JS sẵn có, không thay cả UI bằng jQuery/HTML cũ |

Không copy bootstrap FastAPI `main.py` hoặc endpoint khởi tạo toàn bộ model của project gốc vào server hiện tại. Các adapter nối đúng engine của demo, tránh tạo thêm runtime/index hoặc mở lại scope cũ. Bốn module DB/schema liên quan đã có từ lần chuyển W6; lần này nối phần đã đáp ứng W8 vào đường chạy, không chỉ sao chép file nằm trên đĩa.

## Luồng chạy

1. UI gọi POST `/api/session/start-session` hoặc đọc GET `/api/session/get-sessions`, khôi phục session ID từ localStorage.
2. UI POST `/api/chat` với question/domain/mode/session_id/request_id. Bỏ session_id vẫn chạy stateless để giữ compatibility cho các smoke/baseline cũ.
3. Server ghi Demo_Turns trạng thái processing; request trùng hoặc phiên đang xử lý trả 409. Mỗi session chỉ một lượt đang xử lý.
4. Worker giữ lock engine như trước. Với agentic, memory của đúng phiên được đưa vào GraphOrchestrator; current question chưa chèn vào Chat_Messages nên không bị lặp trong context. Baseline W3–W5 vẫn xử lý truy vấn độc lập.
5. Các sự kiện graph/retrieval/grade/check được chuyển qua SSE và hiển thị tiến trình. Đây là **stage-event streaming**, không stream token LLM. Không tạo đáp án giả khi provider lỗi.
6. Khi có final, lưu nguyên answer, nguồn được dẫn, ứng viên truy xuất, citation offset và trace. Cặp user/bot + references + metadata lượt được commit trong một transaction trước khi báo history_status=saved.
7. Nếu lưu DB lỗi, final vẫn được chuyển cho người dùng và cảnh báo history_error riêng; không đổi lỗi DB thành lỗi model. Nếu không có final, chỉ ghi lượt failed, không tạo tin nhắn bot giả.
8. Mở lại phiên đọc lịch sử và payload đã lưu, khôi phục đúng nguồn của từng câu. Nguồn snapshot được mở từ nội dung lưu cùng lượt, không tự thay bằng nội dung index mới.

Thêm bảng **Demo_Turns** làm dữ liệu vận hành (request_id, domain/mode, trạng thái, message IDs, final_json, error_code, timestamps). Giữ nguyên các bảng gốc. Xóa phiên xóa lượt/messages/references bằng cascade; chặn xóa khi đang xử lý. Phiên bị ngắt do server restart được đánh dấu failed/server_restarted, không giả thành hoàn tất.

## Ngắt kết nối và lỗi

- Nút **Dừng theo dõi** hủy fetch của trình duyệt, không hủy lời gọi model hoặc vòng agent ở máy chủ. Worker vẫn có thể hoàn tất và lưu; mở/tải lại lịch sử để xem. Không tự reconnect rồi gọi LLM trùng.
- Heartbeat SSE không phải đáp án. Parser bỏ comment, giữ Unicode qua byte split, báo lỗi frame JSON hỏng hoặc bị cắt giữa chừng.
- Giữ nguyên pipeline 2 lĩnh vực/53 văn bản, hai vòng retrieval, best iteration, full chunk+BERT, fail-open, điều kiện sinh lại và citation 0-based agent/1-based baseline. BM25 vẫn chỉ ở baseline W4/W5.
- Đây là ứng dụng một người dùng chạy loopback. Có history không đồng nghĩa có đăng nhập, ownership theo user hoặc triển khai nhiều người an toàn. Không bật global User_Facts, dù bảng tương thích vẫn tồn tại.

## Code và cách chạy

- [app.py](app.py), [app.js](app.js), [sse.js](sse.js), [index.html](index.html), [style.css](style.css).
- [History adapter](source/data/db/demo_history.py), [agent bridge](source/agent/demo_agentic.py), [runtime](runtime.py).
- [Bằng chứng W8](Evidence/W08/README.md), [kiểm thử](tests/run_w8_tests.py), [browser test](tests/browser_w8.cjs).

```powershell
# Chạy demo thật, dùng model/profile AWS đã cấu hình riêng:
.\Start-Demo.ps1
# Trình duyệt: http://127.0.0.1:8086

# Kiểm thử W8 + regression W6/baseline, không gọi AWS/model thật:
.\.venv\Scripts\python.exe -B tests/run_w8_tests.py
node tests/test_sse_w8.cjs
python tests/validate_w8.py
```

Không cần sửa .env để dùng history. Có thể đặt `LEGALQA_HISTORY_PATH` thành đường dẫn DB riêng trước khi khởi động. Không trỏ đến DB gốc. File DB riêng, runs, backup và browser tool cache được bỏ qua bởi .gitignore. Không tự xuất lịch sử thật thành evidence.

Browser acceptance dùng `tests/w8_fixture_server.py` trong terminal riêng, đọc URL tạm ở runs/w8/fixture-server.json. Cài `playwright-core@1.56.1` vào thư mục test tools riêng và đặt NODE_PATH tương ứng, rồi chạy `node tests/browser_w8.cjs`. Test yêu cầu Chrome đã cài, xác nhận API có fixture_execution=true trước khi xóa dữ liệu test. Không chạy delete tests với app thật. Dừng fixture server sau kiểm tra.

## Mức xác nhận

Đã kiểm tra SQLite, server HTTP/SSE, agent control flow với model fixture, browser history/source UI và bộ hội thoại synthetic. Kết quả chi tiết ở Evidence/W08. Đây không phải lượt đo Recall@k mới, chất lượng hội thoại nhiều lượt hoặc grounding/refusal với Nova thật. Không sửa/giả số liệu W3–W7 đã khóa. Khả năng chạy toàn bộ graph với model/AWS thật vẫn phụ thuộc môi trường và chưa được kiểm tra trong lượt W8 này.


## Bản xuất bản trên main

App W8 chạy từ gốc repo. `/api/evaluation` giữ đường dẫn runs/evaluation và fallback Evidence/_shared để hiển thị kết quả W3–W5 đã khóa. Các bytes runtime/navigation/validator mà manifest tuần cũ tham chiếu được lưu chính xác trong Evidence/_history. Validator phân biệt file hiện hành với file lịch sử theo week/path/hash; không cập nhật hash cũ thành code mới. W08 manifest kiểm tra code hiện hành riêng. Local evidence snapshot trước đóng gói được giữ tại Evidence/W08/local_snapshot, không phải đường dẫn để chạy app.
