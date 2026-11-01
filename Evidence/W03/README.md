# W03 — Dense RAG baseline trên 100 QA

Thời gian kế hoạch: **11/10–17/10/2026**. Thực nghiệm chung: **31/10/2026**. Đóng gói GitHub và kiểm tra lại: **01/11/2026**; không backdate lịch sử Git.

## Phương pháp và kết quả

PyVi → checkpoint embedding 768 chiều, normalize → Qdrant cosine, top-50. Domain filter lấy từ nhãn QA, một query/câu. Baseline 100 QA là subset của lượt đo chung **31/10/2026**, không phải bằng chứng phép đo đã được chạy trong 11–17/10.

Recall@1 = 67%, @3 = 77%, @5 = 82%, @10 = 85%, @20 = 90%, @50 = 93%; MRR@50 = 0,7357. [QA baseline](../_shared/data/qa_baseline_100.jsonl). Recall bằng Hit trên một Điều nhãn/câu, không đánh giá mọi căn cứ hợp lệ. Prototype có cấu hình Nova Micro nhưng đóng gói này không chạy lại chat, không cung cấp đánh giá đáp án sinh hoặc nghiệm thu UI.


## Đọc và kiểm tra evidence

`metrics.csv` lưu số thực 0–1 cho recall/MRR, không phải phần trăm; cột `unit`, `n`, `k`, `domain` xác định phép đo. `test-results.json` là kiểm tra offline dữ liệu/evidence ngày 01/11/2026, **không phải model inference mới hoặc chấm đúng pháp luật**. `manifest.json` khóa hash artifact và nối tới snapshot chung.

Từ gốc repo: `python Evidence/tools/validate_evidence.py`. Không cần model, GPU hoặc AWS. Dữ liệu quan sát chung được lưu nguyên bytes tại `../_shared/measurement_20261031/`. Xem [hướng dẫn snapshot và tái lập](../_shared/README.md).

## Giới hạn

Phạm vi 53 văn bản, hai domain; mốc tham chiếu 01/07/2026 chưa được kiểm chứng hiệu lực đầy đủ. Một Điều nhãn/câu nên Recall@k = Hit@k trên nhãn đó; k là chunk, không phải Điều duy nhất. Nhãn/relevant set chưa được rà đầy đủ, dev chứa pilot và không phải independent test. Domain lấy sẵn từ QA, chưa đo routing. Chưa xác định overlap với train. Điểm retrieval không chứng minh đáp án hoặc Khoản/Điểm đúng pháp lý; không có lời gọi Nova/web trong benchmark.
