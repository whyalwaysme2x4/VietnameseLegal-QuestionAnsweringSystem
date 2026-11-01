# Dữ liệu và snapshot thực nghiệm dùng chung

`data/` chứa corpus v1 có cấu trúc và các tập QA đã dùng. `measurement_20261031/` giữ nguyên bytes của kết quả lượt đo 31/10/2026. `source_snapshot/` giữ code/config đầu vào theo hash của lượt đo, phục vụ đối chiếu implementation, không phải một ứng dụng chạy độc lập ngay tại thư mục này.

`inventory.json` kê SHA-256 của toàn bộ file dùng chung. Dataset DOCX gốc nằm ở `../../dataset/` từ thư mục `Evidence`, đã có trên repo. Không đưa model weights, index Qdrant, vector cache, phiên chat, file `.env` hoặc credential vào Git.

## Kiểm tra số liệu không cần model

Từ gốc repo chạy `python Evidence/tools/validate_evidence.py`. Validator chỉ dùng Python standard library: kiểm tra hash nguồn, corpus, quan hệ cha-con, spans, nhãn, thứ hạng và tính lại các chỉ số. Không import runtime, tải model hoặc gọi AWS. Đây là tái tính số liệu từ output đã lưu, không phải chạy lại inference.

## Chạy lại inference khi cần một thực nghiệm mới

Chuẩn bị một workspace tạm riêng: sao chép nội dung `source_snapshot/` làm gốc; bổ sung các file `data/` dùng chung; sao chép 53 DOCX ở `dataset/` và đặt hai metadata JSON về thư mục domain tương ứng. Chuẩn bị dependency theo requirements, tải model theo `models.json`/`download_models.py`, tạo một index mới đúng corpus/model fingerprint. Đọc `runtime.py` và `evaluate.py` trước khi chạy. Tắt khởi tạo LLM cho benchmark retrieval; lượt đo gốc đã thay `Engine.refresh_llm` bằng hàm trả False trong tiến trình, không sửa file source. Việc chạy lại inference có thể tốn thời gian và không thuộc lượt đóng gói evidence này.

Không dùng index cũ nếu corpus/model khác hash. Muốn khớp lượt đo phải giữ revisions, PyVi, normalize embedding, cosine, domain filter và candidate budget. Kết quả hiện tại dùng query-vector cache fingerprint khớp; latency không tính query embedding. W4 top-50 mỗi nhánh; W5 top-25 mỗi nhánh, RRF → 20 ứng viên → top-5.

Các QA là dev, chứa pilot, một Điều nhãn/câu và chờ human review. Source URL/ngày hiệu lực còn thiếu; snapshot 01/07/2026 chưa được kiểm chứng pháp lý đầy đủ. Nine parser warnings được giữ trong `data/validation.json`.
