# W01 — Phạm vi, corpus plan và QA pilot

Tuần kế hoạch: **27/09–03/10/2026**. Folder bổ sung ngày **05/11/2026**, trên cùng `main`.

## Nội dung folder

- `code/`: bản sao nguyên file code liên quan; không sửa thuật toán hoặc file gốc.
- `data/`: dữ liệu/QA phục vụ nội dung tuần. Corpus/DOCX dùng chung vẫn ở gốc project.
- `metrics.csv`, `test-results.json`, `figures/`: sao chép nguyên bytes từ [Evidence/W01](../Evidence/W01/README.md).
- `manifest.json`: nguồn từng file, commit nguồn, SHA-256 và kích thước để đối chiếu.

## Đọc code theo nội dung tuần

| File nguồn | Phần liên quan |
|---|---|
| [ingest.py](code/ingest.py) | `SCOPE`, lựa chọn 53 DOCX và metadata snapshot trong `main()`; file dùng chung với W2, còn chứa parser/chunker của W2. |
| [source/core/corpus_scope.json](data/corpus_scope.json) | Danh sách hai lĩnh vực và 53 định danh văn bản, sao chép vào `data/corpus_scope.json`; đây là schema hiện hành, không khẳng định file đã được viết trong W1. |

W1 chủ yếu chốt phạm vi, nguồn, corpus plan, ethics/scope và evaluation protocol; chưa cần chatbot/agent. Xem báo cáo gốc tại [báo cáo W1](../docs/Bao_cao_tuan_W1_Corpus_QA_Evaluation.md). 53 DOCX vẫn dùng chung tại [dataset](../dataset/).

## Cách dùng bản sao

Đây là bản phân loại **code hiện tại theo nội dung từng tuần**, không phải phục hồi các commit cuối tuần trong quá khứ. File dùng chung được giữ nguyên nên có thể chứa cả nhánh của tuần sau; bảng trên chỉ rõ phần cần xem. Không backdate lịch sử hoặc coi ngày tuần là ngày tạo file.

`code/` là bản sao để giảng viên đọc/đối chiếu, không phải một ứng dụng độc lập đã được kiểm thử chạy trong folder này. Đường dẫn dữ liệu/model bên trong code giữ nguyên theo project gốc. Chạy demo và test từ [gốc project](../README.md), không chạy trực tiếp các script trong code/.

## Kiểm chứng và giới hạn

`python verify_week_folders.py` tại gốc repo kiểm tra hash toàn bộ bản sao; không import runtime, tải model hoặc gọi AWS. Các kiểm tra của ứng dụng vẫn chạy từ gốc theo README. Model weights, index, .env thật, database chat và credentials không nằm trong bản sao.

Snapshot 01/07/2026 là mốc tham chiếu; tình trạng hiệu lực và nhãn QA vẫn cần rà soát. Metrics/trace giữ nguyên nguồn, không phải lượt đo mới khi tạo folder tuần. [Xem sáu tuần](../WEEKS.md).
