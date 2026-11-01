# Hệ thống hỏi đáp pháp luật Việt Nam

Bằng chứng tiến độ W1–W5 cho hệ thống hỏi đáp pháp luật hai lĩnh vực. Xem [Evidence theo tuần](Evidence/README.md).

## Phạm vi đã chốt

- Hai lĩnh vực: Giao thông vận tải và Lao động – tiền lương.
- Snapshot date pháp lý: **01/07/2026**.
- Corpus: **53 văn bản DOCX** (38 giao thông, 15 lao động).
- QA pilot: **50 câu** (25 câu mỗi lĩnh vực).

## Bằng chứng W1

- [Báo cáo tiến độ W1](docs/Bao_cao_tuan_W1_Corpus_QA_Evaluation.md): corpus plan, evaluation protocol, ethics/scope note và 50 QA pilot.
- [Bộ QA pilot dạng CSV](data/qa_pilot_50.csv): câu hỏi, đáp án tham chiếu, điều khoản và tệp corpus.
- `dataset/giaoThong_VanTai/`: 38 văn bản.
- `dataset/laoDong_TienLuong/`: 15 văn bản.

Bộ QA hiện ở mức **pilot**. Báo cáo W1 chưa có điểm benchmark thực nghiệm; việc kiểm chứng chi tiết tình trạng hiệu lực, sửa đổi và metadata của từng văn bản được nêu là công việc tiếp theo trong báo cáo.

## Theo dõi evidence từ W4

[Evidence theo tuần](Evidence/README.md) tập hợp corpus, metrics, kiểm tra offline, figures và manifest. Thực nghiệm chung ngày 31/10/2026; tổ chức GitHub bổ sung ngày 01/11/2026. Milestone/issue/PR ghi rõ người thực hiện và reviewer dự kiến. Review của Đỗ Văn Đức đang chờ GitHub username; chưa được coi là đã nghiệm thu.
