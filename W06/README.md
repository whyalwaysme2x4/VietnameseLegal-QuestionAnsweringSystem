# W06 — Agent graph Planner/Grader/Checker, BERT và LangGraph trace

Tuần kế hoạch: **01/11–07/11/2026**. Folder bổ sung ngày **05/11/2026**, trên cùng `main`.

## Nội dung folder

- `code/`: bản sao nguyên file code liên quan; không sửa thuật toán hoặc file gốc.
- `data/`: dữ liệu/QA phục vụ nội dung tuần. Corpus/DOCX dùng chung vẫn ở gốc project.
- `metrics.csv`, `test-results.json`, `figures/`: sao chép nguyên bytes từ [Evidence/W06](../Evidence/W06/README.md).
- `manifest.json`: nguồn từng file, commit nguồn, SHA-256 và kích thước để đối chiếu.

## Đọc code theo nội dung tuần

| File nguồn | Phần liên quan |
|---|---|
| [source/agent/demo_agentic.py](code/source/agent/demo_agentic.py) | Composition root của các agent, BERT, CrossEncoder và scoped Qdrant; Nova Converse adapter. |
| [source/agent/graph_orchestrator.py](code/source/agent/graph_orchestrator.py) | LangGraph Planner → retrieve → extract → grader → select_best → generate → checker → finish/regenerate. |
| [source/agent/planner.py](code/source/agent/planner.py) | Định tuyến theo hai lĩnh vực/53 văn bản; chỉ thu hẹp prompt, giữ logic lớp gốc. |
| [source/agent/orchestrator.py](code/source/agent/orchestrator.py) | Bản tham chiếu chính sách gốc: tổng hai vòng, best iteration, full chunk+BERT, citation 0-based và regeneration một lần. |
| [source/model/extract_model.py](code/source/model/extract_model.py) | Nạp BERT QA; extraction tại `source/extract/utils_extract.py`. |
| [source/search/scoped_qdrant.py](code/source/search/scoped_qdrant.py) | Index riêng và allowlist 53 văn bản, alias filter metadata legacy. |
| [tests/test_agent_w6.py](code/tests/test_agent_w6.py) | 15 ca fixture đối chiếu GraphOrchestrator và Orchestrator; runner ghi kết quả vào runs/w6 ở project gốc. |

Luồng W6 giữ multi-query Dense/RRF của agent gốc, không chèn BM25; BM25 vẫn ở baseline W4/W5. 15 case là fixture control-flow tests, không phải benchmark model hoặc full AWS demo. Smoke thật riêng đã nạp BERT và chạy một extraction, nạp CrossEncoder nhưng chưa prediction CE; full AWS chưa xác nhận.

## Cách dùng bản sao

Đây là bản phân loại **code hiện tại theo nội dung từng tuần**, không phải phục hồi các commit cuối tuần trong quá khứ. File dùng chung được giữ nguyên nên có thể chứa cả nhánh của tuần sau; bảng trên chỉ rõ phần cần xem. Không backdate lịch sử hoặc coi ngày tuần là ngày tạo file.

`code/` là bản sao để giảng viên đọc/đối chiếu, không phải một ứng dụng độc lập đã được kiểm thử chạy trong folder này. Đường dẫn dữ liệu/model bên trong code giữ nguyên theo project gốc. Chạy demo và test từ [gốc project](../README.md), không chạy trực tiếp các script trong code/.

Khi chạy project gốc, chọn mode **`agentic`** để xem luồng của tuần này.

## Kiểm chứng và giới hạn

`python verify_week_folders.py` tại gốc repo kiểm tra hash toàn bộ bản sao; không import runtime, tải model hoặc gọi AWS. Các kiểm tra của ứng dụng vẫn chạy từ gốc theo README. Model weights, index, .env thật, database chat và credentials không nằm trong bản sao.

Snapshot 01/07/2026 là mốc tham chiếu; tình trạng hiệu lực và nhãn QA vẫn cần rà soát. Metrics/trace giữ nguyên nguồn, không phải lượt đo mới khi tạo folder tuần. [Xem sáu tuần](../WEEKS.md).
