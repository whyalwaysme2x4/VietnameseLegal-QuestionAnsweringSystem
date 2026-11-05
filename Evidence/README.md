# Evidence theo tuần

| Tuần | Nội dung | Minh chứng |
|---|---|---|
| W01 | Scope/corpus plan, ethics, 50 QA pilot | [W01](W01/README.md) |
| W02 | Parser Điều/Khoản/Điểm, metadata, corpus v1 | [W02](W02/README.md) |
| W03 | Dense baseline, 100 QA | [W03](W03/README.md) |
| W04 | BM25/Dense + RRF, 150 QA dev | [W04](W04/README.md) |
| W05 | CrossEncoder paired ablation, 200 QA dev | [W05](W05/README.md) |
| W06 | Agent graph, BERT, 15 fixture cases và trace | [W06](W06/README.md) |

Mỗi tuần có README, metrics.csv, test-results.json, figures và manifest.json. W01–W03 là evidence được tổ chức bổ sung ngày 01/11/2026; kết quả W03 là subset của lượt đo 31/10/2026. Không suy ra lịch sử issue/review hoặc ngày thực nghiệm từ số tuần.

Tất cả W01–W06 nằm trên **main**. W1–W5 đã merge qua các PR lịch sử; W6 cập nhật trực tiếp main theo yêu cầu ngày 05/11/2026, không tạo nhánh hoặc PR riêng. Quang thực hiện; Đức (`dovanduc2004`) kiểm tra/review. Review W6 đang chờ, không ghi approval tự động. Snapshot tag khóa nội dung, không thay review.

Chạy `python Evidence/tools/validate_evidence.py` từ gốc repo. Không tải model hoặc gọi AWS. [Nguồn chung và cách tái lập](_shared/README.md).

[Theo dõi milestone, issue, review và snapshot của sáu tuần](GITHUB_TRACKING.md). Thông tin chờ merge/review trong README/manifest snapshot W1–W5 phản ánh thời điểm đóng gói trước đây; trạng thái hiện hành xem bảng theo dõi này.

W6 có validator riêng: `python Evidence/tools/validate_w06.py`. Trace và pass rate W6 là fixture control-flow tests; chưa chạy full AWS agent. Không trộn với retrieval metrics W3–W5. Chạy lại thử nghiệm ghi vào `runs/`, không ghi đè evidence.
