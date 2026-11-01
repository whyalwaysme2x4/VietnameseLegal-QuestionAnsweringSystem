# W01 — Phạm vi, corpus plan và QA pilot

Thời gian kế hoạch: **27/09–03/10/2026**. Thực nghiệm chung: **31/10/2026**. Đóng gói GitHub và kiểm tra lại: **01/11/2026**; không backdate lịch sử Git.

## Kết quả có thể đối chiếu

53 DOCX = 38 giao thông + 15 lao động; 50 QA pilot. Báo cáo W1 hiện có tại [docs/Bao_cao_tuan_W1_Corpus_QA_Evaluation.md](../../docs/Bao_cao_tuan_W1_Corpus_QA_Evaluation.md), bao gồm corpus plan, evaluation protocol và ethics/scope note. QA pilot CSV tại [data/qa_pilot_50.csv](../../data/qa_pilot_50.csv).

`metrics.csv` là thống kê inventory kiểm tra ngày 01/11/2026, không phải điểm chất lượng mô hình đo trong W1. Chưa có bằng chứng review chéo lịch sử W1 trong GitHub.


## Theo dõi trên GitHub

- [Milestone Tuan1](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/3).
- [Issue thực hiện của Tăng Minh Quang](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/7).
- [Issue kiểm tra/review của Đỗ Văn Đức](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/8).
- Nhánh: `evidence/w01`. Snapshot tuần: `w01`.
- Đỗ Văn Đức (`@dovanduc2004`) phụ trách kiểm tra kết quả/review. Trạng thái truy cập: `collaborator_confirmed`. Review thực tế vẫn chưa hoàn tất.
- Trạng thái: **chờ review thực tế**, chưa nghiệm thu hoặc merge thay reviewer.
- PR: https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/13.
- Các PR W01–W03 bổ sung quản lý/review cho evidence đã có, dựa trên nền chung trong [PR #5](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/5); không tạo lịch sử giả cho các tuần trước.


## Đọc và kiểm tra evidence

`metrics.csv` lưu số thực 0–1 cho recall/MRR, không phải phần trăm; cột `unit`, `n`, `k`, `domain` xác định phép đo. `test-results.json` là kiểm tra offline dữ liệu/evidence ngày 01/11/2026, **không phải model inference mới hoặc chấm đúng pháp luật**. `manifest.json` khóa hash artifact và nối tới snapshot chung.

Từ gốc repo: `python Evidence/tools/validate_evidence.py`. Không cần model, GPU hoặc AWS. Dữ liệu quan sát chung được lưu nguyên bytes tại `../_shared/measurement_20261031/`. Xem [hướng dẫn snapshot và tái lập](../_shared/README.md).

## Giới hạn

Phạm vi 53 văn bản, hai domain; mốc tham chiếu 01/07/2026 chưa được kiểm chứng hiệu lực đầy đủ. Một Điều nhãn/câu nên Recall@k = Hit@k trên nhãn đó; k là chunk, không phải Điều duy nhất. Nhãn/relevant set chưa được rà đầy đủ, dev chứa pilot và không phải independent test. Domain lấy sẵn từ QA, chưa đo routing. Chưa xác định overlap với train. Điểm retrieval không chứng minh đáp án hoặc Khoản/Điểm đúng pháp lý; không có lời gọi Nova/web trong benchmark.
