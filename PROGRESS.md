# Tiến độ hiện hành — W01–W08 trên main

Cập nhật 25/11/2026. [Code/data từng tuần](WEEKS.md), [W08](W08/README.md) và [hướng dẫn chạy](W8_IMPLEMENTATION.md).

| W8 | Evidence |
|---|---|
| SSE frontend + SQLite history, integrated app | [README W08](Evidence/W08/README.md) |
| 46/46 Python tests, 8/8 parser, 8/8 Chrome checks | [Kết quả](Evidence/W08/test-results.json), [browser](Evidence/W08/browser-results.json) |
| 12 hội thoại / 36 lượt / 72 tin nhắn synthetic | [Dữ liệu](Evidence/W08/synthetic_conversations.json), [logs](Evidence/W08/synthetic_chat_logs.jsonl) |
| Code/evidence/hash và hình UI | [Manifest](Evidence/W08/manifest.json), [ảnh](Evidence/W08/figures/) |
| Milestone Tuan8, Quang thực hiện, Đức review | [Tracking](Evidence/W08/github.json) |

Đã tích hợp app W8 tại gốc, dùng DB riêng không commit. Không bật authentication/global facts hoặc thay kỹ thuật retrieval/citation/agent policy. Test fixture không phải live AWS/model benchmark. Review Đức đang chờ, không có PR/approval W8 theo phương án cập nhật trực tiếp main.

W7 policy/protocol và QA draft vẫn tại [Evidence/W07](Evidence/W07/README.md); semantic grounding/refusal metrics thật chưa được giải quyết bằng W8. Các evidence/manifest/trace W01–W07 và folder tuần cũ giữ nguyên; code/input lịch sử mà root mới thay đổi nằm tại [Evidence/_history](Evidence/_history/README.md). Validator kiểm tra đúng phiên bản theo hash thay vì sửa kết quả cũ.
