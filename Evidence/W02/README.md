# W02 — Parser Điều/Khoản/Điểm và corpus v1

Thời gian kế hoạch: **04/10–10/10/2026**. Thực nghiệm chung: **31/10/2026**. Đóng gói GitHub và kiểm tra lại: **01/11/2026**; không backdate lịch sử Git.

## Kết quả có thể đối chiếu

Parser đọc DOCX thành text, tách cấu trúc Điều → Khoản → Điểm, giữ parent ID, offset và nội dung gốc rồi tạo chunk/metadata. Snapshot code: [ingest.py](../_shared/source_snapshot/ingest.py). Corpus: [documents](../_shared/data/documents.jsonl), [legal_nodes](../_shared/data/legal_nodes.jsonl), [chunks](../_shared/data/chunks.jsonl).

Đã có 1.776 Điều, 6.527 Khoản, 6.632 Điểm và 6.883 chunk; đọc 15 bảng. Giữ lại 9 cảnh báo trùng số để rà soát. Không đồng nhất kiểm tra parent/spans với xác nhận parser chính xác mọi trường hợp hoặc hiệu lực pháp luật. Chưa có kết quả đánh giá thủ công parser và review GitHub lịch sử W2.


## Theo dõi trên GitHub

- [Milestone Tuan2](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/4).
- [Issue thực hiện của Tăng Minh Quang](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/9).
- [Issue kiểm tra/review của Đỗ Văn Đức](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/10).
- Nhánh: `evidence/w02`. Snapshot tuần: `w02`.
- Đỗ Văn Đức (`@dovanduc2004`) phụ trách kiểm tra kết quả/review. Trạng thái truy cập: `collaborator_confirmed`. Review thực tế vẫn chưa hoàn tất.
- Trạng thái: **chờ review thực tế**, chưa nghiệm thu hoặc merge thay reviewer.
- PR: https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/14.
- Các PR W01–W03 bổ sung quản lý/review cho evidence đã có, dựa trên nền chung trong [PR #5](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/5); không tạo lịch sử giả cho các tuần trước.


## Đọc và kiểm tra evidence

`metrics.csv` lưu số thực 0–1 cho recall/MRR, không phải phần trăm; cột `unit`, `n`, `k`, `domain` xác định phép đo. `test-results.json` là kiểm tra offline dữ liệu/evidence ngày 01/11/2026, **không phải model inference mới hoặc chấm đúng pháp luật**. `manifest.json` khóa hash artifact và nối tới snapshot chung.

Từ gốc repo: `python Evidence/tools/validate_evidence.py`. Không cần model, GPU hoặc AWS. Dữ liệu quan sát chung được lưu nguyên bytes tại `../_shared/measurement_20261031/`. Xem [hướng dẫn snapshot và tái lập](../_shared/README.md).

## Giới hạn

Phạm vi 53 văn bản, hai domain; mốc tham chiếu 01/07/2026 chưa được kiểm chứng hiệu lực đầy đủ. Một Điều nhãn/câu nên Recall@k = Hit@k trên nhãn đó; k là chunk, không phải Điều duy nhất. Nhãn/relevant set chưa được rà đầy đủ, dev chứa pilot và không phải independent test. Domain lấy sẵn từ QA, chưa đo routing. Chưa xác định overlap với train. Điểm retrieval không chứng minh đáp án hoặc Khoản/Điểm đúng pháp lý; không có lời gọi Nova/web trong benchmark.
