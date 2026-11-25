# W08 — SSE frontend, history và ứng dụng tích hợp

Tuần kế hoạch 15/11–21/11/2026; thực hiện/xuất bản 25/11/2026, cùng main.

- `code/`: các file app/UI/SSE/history, agent bridge, module DB gốc và tests liên quan W8, sao chép nguyên bytes từ bản xuất bản.
- `data/`: 12 cuộc hội thoại synthetic và 72 tin nhắn fixture; không private DB.
- `metrics.csv`, `test-results.json`, `figures/`, `manifest.json`: minh chứng cùng [Evidence/W08](../Evidence/W08/README.md).

| Đọc code | Nội dung |
|---|---|
| [app.py](code/app.py), [app.js](code/app.js), [sse.js](code/sse.js) | SSE stage events, session APIs, frontend stream/history |
| [demo_history.py](code/source/data/db/demo_history.py) | SQLite adapter, atomic save, request/state tracking và snapshot nguồn |
| [demo_agentic.py](code/source/agent/demo_agentic.py), [runtime.py](code/runtime.py) | Nối memory đúng session; baseline vẫn độc lập |
| [test_w8_history.py](code/tests/test_w8_history.py) | Lỗi provider/DB, disconnect, citation, session isolation và reload |
| [browser_w8.cjs](code/tests/browser_w8.cjs) | Chrome acceptance với fixture server và DB tạm |

46 Python tests, 8 parser checks, 8 Chrome checks và 36 roundtrips đạt với fixture. Không phải chất lượng pháp luật/model thật. Folder này không được kiểm thử như app độc lập; chạy từ [gốc repo](../README.md) theo [hướng dẫn W8](../W8_IMPLEMENTATION.md). Nội dung là code hiện hành phân loại theo tuần, không backdate release lịch sử. [Mục lục](../WEEKS.md).
