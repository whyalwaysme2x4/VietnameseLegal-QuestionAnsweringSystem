# W05 — CrossEncoder reranking và rerank ablation

Tuần kế hoạch: **25/10–31/10/2026**. Folder bổ sung ngày **05/11/2026**, trên cùng `main`.

## Nội dung folder

- `code/`: bản sao nguyên file code liên quan; không sửa thuật toán hoặc file gốc.
- `data/`: dữ liệu/QA phục vụ nội dung tuần. Corpus/DOCX dùng chung vẫn ở gốc project.
- `metrics.csv`, `test-results.json`, `figures/`: sao chép nguyên bytes từ [Evidence/W05](../Evidence/W05/README.md).
- `manifest.json`: nguồn từng file, commit nguồn, SHA-256 và kích thước để đối chiếu.

## Đọc code theo nội dung tuần

| File nguồn | Phần liên quan |
|---|---|
| [source/model/rerank_model_finetune.py](code/source/model/rerank_model_finetune.py) | Nạp CrossEncoder checkpoint fine-tuned; giữ wrapper gốc. |
| [source/rerank/utils_rerank.py](code/source/rerank/utils_rerank.py) | `rerank_documents_finetune()` dự đoán score query–document và lấy top-5. |
| [runtime.py](code/runtime.py) | `rerank_candidates()` và `chat(mode="rerank")`; W5 top-25/nhánh → RRF → 20 ứng viên → CE top-5, override max_length 512/batch 4 của baseline. |
| [evaluate.py](code/evaluate.py) | Hai nhánh `w5_without_ce`/`w5_with_ce` dùng cùng pool 20 ứng viên; giữ kết quả suy giảm đã đo, không thay số liệu. |
| [prepare_qa.py](code/prepare_qa.py) | Chuẩn bị 200 QA dev từ nguồn có citation; nhãn vẫn pending human review. |

Kết quả W5 thuộc baseline BM25/Dense + RRF, không phải agent W6. Code hiện hành có nhánh W6 và models.json có BERT; BERT không thuộc nhánh baseline `rerank` của W5. Chưa dùng điểm này để kết luận chất lượng pháp lý.

## Cách dùng bản sao

Đây là bản phân loại **code hiện tại theo nội dung từng tuần**, không phải phục hồi các commit cuối tuần trong quá khứ. File dùng chung được giữ nguyên nên có thể chứa cả nhánh của tuần sau; bảng trên chỉ rõ phần cần xem. Không backdate lịch sử hoặc coi ngày tuần là ngày tạo file.

`code/` là bản sao để giảng viên đọc/đối chiếu, không phải một ứng dụng độc lập đã được kiểm thử chạy trong folder này. Đường dẫn dữ liệu/model bên trong code giữ nguyên theo project gốc. Chạy demo và test từ [gốc project](../README.md), không chạy trực tiếp các script trong code/.

Khi chạy project gốc, chọn mode **`rerank`** để xem luồng của tuần này.

## Kiểm chứng và giới hạn

`python verify_week_folders.py` tại gốc repo kiểm tra hash toàn bộ bản sao; không import runtime, tải model hoặc gọi AWS. Các kiểm tra của ứng dụng vẫn chạy từ gốc theo README. Model weights, index, .env thật, database chat và credentials không nằm trong bản sao.

Snapshot 01/07/2026 là mốc tham chiếu; tình trạng hiệu lực và nhãn QA vẫn cần rà soát. Metrics/trace giữ nguyên nguồn, không phải lượt đo mới khi tạo folder tuần. [Xem sáu tuần](../WEEKS.md).
