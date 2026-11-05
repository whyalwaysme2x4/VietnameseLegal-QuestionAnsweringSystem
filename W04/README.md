# W04 — Hybrid BM25/Dense + RRF và retrieval comparison

Tuần kế hoạch: **18/10–24/10/2026**. Folder bổ sung ngày **05/11/2026**, trên cùng `main`.

## Nội dung folder

- `code/`: bản sao nguyên file code liên quan; không sửa thuật toán hoặc file gốc.
- `data/`: dữ liệu/QA phục vụ nội dung tuần. Corpus/DOCX dùng chung vẫn ở gốc project.
- `metrics.csv`, `test-results.json`, `figures/`: sao chép nguyên bytes từ [Evidence/W04](../Evidence/W04/README.md).
- `manifest.json`: nguồn từng file, commit nguồn, SHA-256 và kích thước để đối chiếu.

## Đọc code theo nội dung tuần

| File nguồn | Phần liên quan |
|---|---|
| [runtime.py](code/runtime.py) | `Engine.lexical()` dùng BM25; `Engine.dense()` dùng dense; `retrieve(mode="hybrid")` hợp nhất bằng RRF; `chat(mode="hybrid")` bỏ bước CE. |
| [source/rerank/utils_rerank.py](code/source/rerank/utils_rerank.py) | `reciprocal_rank_fusion()` hợp nhất theo thứ hạng; cùng file còn chứa hàm rerank của W5, không gọi ở mode hybrid. |
| [evaluate.py](code/evaluate.py) | So sánh `dense`, `bm25`, `hybrid_rrf` trên 150 QA dev; đọc cấu hình đo và output gốc trong Evidence/W04. |

Giữ kết quả so sánh đã đo, không chạy lại inference. Runtime hiện hành và evaluator là file dùng chung nhiều tuần. QA dev chứa pilot; Recall@k dựa trên nhãn Điều chính chưa rà soát đầy đủ.

## Cách dùng bản sao

Đây là bản phân loại **code hiện tại theo nội dung từng tuần**, không phải phục hồi các commit cuối tuần trong quá khứ. File dùng chung được giữ nguyên nên có thể chứa cả nhánh của tuần sau; bảng trên chỉ rõ phần cần xem. Không backdate lịch sử hoặc coi ngày tuần là ngày tạo file.

`code/` là bản sao để giảng viên đọc/đối chiếu, không phải một ứng dụng độc lập đã được kiểm thử chạy trong folder này. Đường dẫn dữ liệu/model bên trong code giữ nguyên theo project gốc. Chạy demo và test từ [gốc project](../README.md), không chạy trực tiếp các script trong code/.

Khi chạy project gốc, chọn mode **`hybrid`** để xem luồng của tuần này.

## Kiểm chứng và giới hạn

`python verify_week_folders.py` tại gốc repo kiểm tra hash toàn bộ bản sao; không import runtime, tải model hoặc gọi AWS. Các kiểm tra của ứng dụng vẫn chạy từ gốc theo README. Model weights, index, .env thật, database chat và credentials không nằm trong bản sao.

Snapshot 01/07/2026 là mốc tham chiếu; tình trạng hiệu lực và nhãn QA vẫn cần rà soát. Metrics/trace giữ nguyên nguồn, không phải lượt đo mới khi tạo folder tuần. [Xem sáu tuần](../WEEKS.md).
