# W03 — Dense RAG baseline và chat prototype

Tuần kế hoạch: **11/10–17/10/2026**. Folder bổ sung ngày **05/11/2026**, trên cùng `main`.

## Nội dung folder

- `code/`: bản sao nguyên file code liên quan; không sửa thuật toán hoặc file gốc.
- `data/`: dữ liệu/QA phục vụ nội dung tuần. Corpus/DOCX dùng chung vẫn ở gốc project.
- `metrics.csv`, `test-results.json`, `figures/`: sao chép nguyên bytes từ [Evidence/W03](../Evidence/W03/README.md).
- `manifest.json`: nguồn từng file, commit nguồn, SHA-256 và kích thước để đối chiếu.

## Đọc code theo nội dung tuần

| File nguồn | Phần liên quan |
|---|---|
| [runtime.py](code/runtime.py) | `Engine.dense()` truy vấn vector/Qdrant; `retrieve(mode="dense")`; `chat(mode="dense")` dùng top chunks và gọi Nova Micro. |
| [source/model/embedding_model.py](code/source/model/embedding_model.py) | Wrapper embedding fine-tuned, kết hợp PyVi trong runtime. |
| [app.py](code/app.py) | HTTP/SSE `/api/chat`, source cards và status; frontend ở `index.html`, `app.js`, `style.css`. |
| [evaluate.py](code/evaluate.py) | Phần `dense` và subset `qa_baseline_100.jsonl` trong lượt đo dùng chung W3–W5. |
| [source/generate/synthesis_response.py](code/source/generate/synthesis_response.py) | Kiểm tra output/citation baseline 1-based; khác key 0-based của agent W6. |

100 QA là subset của lượt đo chung ngày 31/10/2026, chứa pilot và nhãn đang chờ rà soát. Code runtime/evaluate/UI được sao chép nguyên file hiện tại nên còn có các nhánh W4–W6; phần W3 cần xem là mode `dense`, không phải toàn bộ file chỉ thuộc W3.

## Cách dùng bản sao

Đây là bản phân loại **code hiện tại theo nội dung từng tuần**, không phải phục hồi các commit cuối tuần trong quá khứ. File dùng chung được giữ nguyên nên có thể chứa cả nhánh của tuần sau; bảng trên chỉ rõ phần cần xem. Không backdate lịch sử hoặc coi ngày tuần là ngày tạo file.

`code/` là bản sao để giảng viên đọc/đối chiếu, không phải một ứng dụng độc lập đã được kiểm thử chạy trong folder này. Đường dẫn dữ liệu/model bên trong code giữ nguyên theo project gốc. Chạy demo và test từ [gốc project](../README.md), không chạy trực tiếp các script trong code/.

Khi chạy project gốc, chọn mode **`dense`** để xem luồng của tuần này.

## Kiểm chứng và giới hạn

`python verify_week_folders.py` tại gốc repo kiểm tra hash toàn bộ bản sao; không import runtime, tải model hoặc gọi AWS. Các kiểm tra của ứng dụng vẫn chạy từ gốc theo README. Model weights, index, .env thật, database chat và credentials không nằm trong bản sao.

Snapshot 01/07/2026 là mốc tham chiếu; tình trạng hiệu lực và nhãn QA vẫn cần rà soát. Metrics/trace giữ nguyên nguồn, không phải lượt đo mới khi tạo folder tuần. [Xem sáu tuần](../WEEKS.md).
