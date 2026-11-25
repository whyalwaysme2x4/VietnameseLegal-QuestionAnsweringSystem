# Hệ thống hỏi đáp pháp luật Việt Nam

Bản demo và minh chứng **W1–W6 cùng trên nhánh `main`**. Giảng viên có thể xem toàn bộ tiến độ tại [Evidence theo tuần](Evidence/README.md), không cần chuyển nhánh. Code hiện hành nằm ở gốc repo; snapshot W4/W5 được giữ nguyên để đối chiếu số liệu.

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

## Tiến độ theo tuần

| Tuần | Nội dung | Minh chứng trên main |
|---|---|---|
| W01 | Corpus plan, ethics/scope, 50 QA pilot | [Evidence/W01](Evidence/W01/README.md) |
| W02 | Parser Điều/Khoản/Điểm, metadata, corpus v1 | [Evidence/W02](Evidence/W02/README.md) |
| W03 | Dense RAG baseline, 100 QA | [Evidence/W03](Evidence/W03/README.md) |
| W04 | BM25/Dense + RRF, 150 QA dev | [Evidence/W04](Evidence/W04/README.md) |
| W05 | CrossEncoder, rerank ablation, 200 QA dev | [Evidence/W05](Evidence/W05/README.md) |
| W06 | Planner/Grader/Checker, BERT, LangGraph trace, 15 agent cases | [Evidence/W06](Evidence/W06/README.md) |

Mỗi thư mục tuần có `README.md`, `metrics.csv`, `test-results.json`, `figures/`, `manifest.json`. [Bảng milestone/issue/review/tag](Evidence/GITHUB_TRACKING.md) ghi trạng thái thật. W1–W5 đã merge; W6 cập nhật trực tiếp main theo yêu cầu mới, không tạo PR/nhánh riêng. Review W6 của Đỗ Văn Đức (`dovanduc2004`) đang chờ; commit/tag không thay thế peer review.

## Chạy demo

Python 3.12, model local theo revision trong `models.json`, AWS Nova Micro qua profile `legalqa-w4`. Không chứa credential hoặc weights/index trong repo.

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-w6-lock.txt
.\.venv\Scripts\python.exe download_models.py
Copy-Item .env.example .env
# Tự cấu hình/đăng nhập AWS profile legalqa-w4 trên máy; không đưa credential vào Git.
.\Start-Demo.ps1
```

Mở `http://127.0.0.1:8086`; dừng bằng `Stop-Demo.ps1`. Khởi động lần đầu ở máy mới tạo embedding/index local nếu chưa có; không tự chạy benchmark. Nếu đã có môi trường và weights, chỉ cần `Start-Demo.ps1`.

Giao diện có W3 Dense, W4 Hybrid, W5 rerank và W6 agentic. W6 dùng **Planner → multi-query Dense → RRF → CrossEncoder → BERT → Grader → Generator → Checker**, giữ chính sách gốc và key citation 0-based. BM25 còn ở W4/W5. Xem [triển khai W6](W6_IMPLEMENTATION.md) và [nguồn tái sử dụng](ATTRIBUTION.md).

## Kiểm tra minh chứng

```powershell
python Evidence/tools/validate_evidence.py
python Evidence/tools/validate_w06.py
.\.venv\Scripts\python.exe -B tests/run_w6_tests.py
```

Hai validator đầu dùng standard library, chỉ kiểm tra artifact/hash và số liệu đã lưu, không tải model/gọi AWS. Test runner cần dependency W6 và ghi kết quả mới vào `runs/w6/`; đánh giá mới ghi `runs/evaluation/`. Evidence đã chốt không bị ghi đè.

15/15 case W6 là **fixture kiểm tra luồng/contract**, không phải 15 câu chạy AWS thật. Smoke riêng đã nạp BERT thật và chạy một extraction; chưa xác nhận full graph live AWS hoặc chất lượng đáp án W6. Số liệu W4/W5 là dev chứa pilot, nhãn/hiệu lực pháp lý pending; không coi là test độc lập hoặc bằng chứng chất lượng agent W6.
