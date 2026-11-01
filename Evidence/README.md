# Evidence theo tuần

| Tuần | Nội dung | Minh chứng |
|---|---|---|
| W01 | Scope/corpus plan, ethics, 50 QA pilot | [W01](W01/README.md) |
| W02 | Parser Điều/Khoản/Điểm, metadata, corpus v1 | [W02](W02/README.md) |
| W03 | Dense baseline, 100 QA | [W03](W03/README.md) |
| W04 | BM25/Dense + RRF, 150 QA dev | [W04](W04/README.md) |

Mỗi tuần có README, metrics.csv, test-results.json, figures và manifest.json. W01–W03 là evidence được tổ chức bổ sung ngày 01/11/2026; kết quả W03 là subset của lượt đo 31/10/2026. Không suy ra lịch sử issue/review hoặc ngày thực nghiệm từ số tuần.

Từ W4: milestone → issue thực hiện + issue review → PR → snapshot tuần. Quang thực hiện; Đức kiểm tra/review, chưa có username. Review đang chờ, không ghi approval tự động. Snapshot tag khóa nội dung, không thay review.

Chạy `python Evidence/tools/validate_evidence.py` từ gốc repo. Không tải model hoặc gọi AWS. [Nguồn chung và cách tái lập](_shared/README.md).
