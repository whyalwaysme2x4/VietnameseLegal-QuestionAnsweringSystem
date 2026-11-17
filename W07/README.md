# W07 — Citation, refusal, grounding và source UI

Tuần kế hoạch 08/11–14/11/2026; đóng gói 17/11/2026 trên main.

- [Evidence chính](../Evidence/W07/README.md): policy, protocol, kết quả fixture, metrics và giới hạn.
- `code/`: bản sao nguyên file từ project hiện hành để đọc theo tuần; không phải app độc lập hoặc bản lịch sử cuối W7.
- `data/`: QA development candidates và data card; 25 synthetic + 5 đối chứng cũ. Nhãn pending, không phải final test.
- `metrics.csv`, `test-results.json`, `figures/`: bản sao evidence mới, không phải đo model thật.
- `manifest.json`: commit/hash nguồn từng file.

## Điểm đọc code

| File trong code/ | Vai trò |
|---|---|
| source/agent/orchestrator.py | Reference generation 0-based, refusal khi không citations, checker và sinh lại |
| source/agent/graph_orchestrator.py | Cùng behavior trong LangGraph; checker chỉ nguồn đã dẫn |
| source/agent/hallucination_checker.py | CheckResult, truncation và parse fail-open |
| source/agent/demo_agentic.py | Mapping nguồn agent sang UI |
| source/generate/synthesis_response.py | Parser baseline 1-based; tách hợp đồng agent |
| app.py, app.js, index.html | Source endpoint, thẻ nguồn, dialog và cảnh báo hiệu lực |
| tests/ | Ca fixture được tái sử dụng, test parser; W7 runner mới nằm tại gốc tests/ |

Code dùng chung giữ nguyên nên có thể chứa bước W3–W6. Chạy app và test từ [gốc repo](../README.md), không chạy trực tiếp code/ trong folder này. W7 không đổi kỹ thuật, citation offset, policy lỗi hoặc ngưỡng agent. [Mục lục các tuần](../WEEKS.md).
