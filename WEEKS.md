# Code và dữ liệu theo tuần

Các folder **W01–W06 nằm ngay thư mục gốc repo**, cùng nhánh `main`. Toàn bộ project đang chạy và `Evidence/` được giữ nguyên; các folder tuần là bản sao bổ sung để đọc code theo nội dung đồ án.

| Folder | Nội dung chính | Điểm bắt đầu đọc code |
|---|---|---|
| [W01](W01/README.md) | Phạm vi 53 văn bản, snapshot, corpus plan, 50 QA pilot | [SCOPE và manifest trong ingest.py](W01/code/ingest.py), [danh sách corpus](W01/data/manifest.json) |
| [W02](W02/README.md) | DOCX → Điều/Khoản/Điểm → metadata → corpus v1 | [ingest.py](W02/code/ingest.py), [corpus đã cấu trúc](W02/data/) |
| [W03](W03/README.md) | Dense RAG baseline, chat, 100 QA | [runtime.py](W03/code/runtime.py): `dense`, `retrieve`, `chat(mode="dense")` |
| [W04](W04/README.md) | BM25/Dense + RRF, comparison, 150 QA dev | [runtime.py](W04/code/runtime.py): `lexical`, `retrieve(mode="hybrid")`; [RRF](W04/code/source/rerank/utils_rerank.py) |
| [W05](W05/README.md) | CrossEncoder, rerank ablation, 200 QA dev | [CrossEncoder](W05/code/source/model/rerank_model_finetune.py), [evaluate.py](W05/code/evaluate.py) |
| [W06](W06/README.md) | Planner/Grader/Checker, BERT, LangGraph, 15 fixture cases | [graph](W06/code/source/agent/graph_orchestrator.py), [composition](W06/code/source/agent/demo_agentic.py), [cases](W06/code/tests/agent_cases_w6.json) |

Mỗi folder có `README.md`, `code/`, `data/`, `metrics.csv`, `test-results.json`, `figures/`, `manifest.json`. W6 còn có các trace/smoke artifacts ở `W06/evidence/`. Manifest ghi đường dẫn nguồn, commit và SHA-256 cho từng bản sao.

Các bản sao lấy từ commit `2a9e02134bdded6993d8d7c547cf8e68b5f7372e` ngày 05/11/2026, **phân loại theo nội dung tuần**, không phải tái dựng phiên bản lịch sử ở cuối từng tuần. File dùng chung được sao chép nguyên vẹn, có thể chứa các nhánh của tuần khác; README chỉ rõ hàm/chế độ cần xem. Không tự loại bớt code hoặc thay thuật toán để giả lập lịch sử.

Đọc code trong folder tuần; **chạy demo từ gốc project** theo [README chính](README.md). Các folder này chưa được kiểm thử như ứng dụng chạy độc lập và vẫn tham chiếu cấu hình dữ liệu/model theo gốc project. Corpus DOCX gốc dùng chung ở `dataset/`; không sao chép weights/index/credential.

Kiểm tra tính toàn vẹn: `python verify_week_folders.py`. Lệnh chỉ đọc file và hash, không tải model, không gọi AWS, không ghi đè evidence. [Evidence gốc](Evidence/README.md) và các tag `w01`–`w06` giữ nguyên. Metrics/trace không phải lượt đo mới; các giới hạn về fixture, dev/pilot và hiệu lực pháp lý vẫn áp dụng.
