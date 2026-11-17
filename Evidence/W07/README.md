# W07 — Citation & refusal policy

Tuần kế hoạch **08/11–14/11/2026**. Gói được chuẩn bị và kiểm tra **17/11/2026**, không backdate. Code/evidence trên main; snapshot dự kiến `w07`. Phạm vi hai lĩnh vực/53 DOCX, snapshot tham chiếu 01/07/2026; hiệu lực từng nguồn chưa xác minh.

## Nội dung nộp

- [Citation/refusal policy](CITATION_REFUSAL_POLICY.md): hợp đồng citation baseline/agent, ma trận answer/clarify/refuse và giới hạn fail-open gốc.
- [Evaluation protocol](EVALUATION_PROTOCOL.md): RQ, metric definitions, lặp lại fixture checks, quy trình model thật chưa thực hiện.
- [Source UI](SOURCE_UI.md): file liên quan, API/dialog, evidence contract và checklist browser.
- [QA candidates](data/README.md): **30 dev candidates** = 25 synthetic + 5 đối chứng dev; trong 25 synthetic có 20 refuse và 5 clarify; nhãn pending, chưa là unanswerable gold độc lập.
- [Kết quả test mới](test-results.json), [trace fixture](traces/), [HTTP/SSE smoke](http-contract-smoke.json), [metrics](metrics.csv), [manifest](manifest.json).
- [Code phân loại theo tuần](../../W07/README.md), [sơ đồ](figures/citation_refusal_flow.mmd), [GitHub tracking](github.json).

## Trạng thái đúng theo bằng chứng

| Hạng mục | Trạng thái |
|---|---|
| Citation mapping, checker, refusal branches, source UI | Implementation kế thừa đã được đối chiếu, không tự thay behavior |
| Test luồng, parser, dữ liệu và source contract | Chạy offline lại; kết quả chi tiết test-results và HTTP smoke |
| Unanswerable QA set | Có draft synthetic+controls, cần human/legal review và mở rộng ca thiếu căn cứ pháp luật |
| Semantic grounding/refusal với Nova | Chưa đo; metrics để trống với status not_measured |
| Browser screenshot/UI visual QA | Chưa thực hiện, không có screenshot giả |
| Independent final test | Chưa đóng băng; tập này là dev candidate |

Không gọi AWS, không train/reindex hoặc sửa runtime. Các file code trong W07 là bản sao để đọc; chạy từ gốc repo. Không coi pass fixture là đúng luật hoặc độ chính xác của Planner/Checker/model. Các test W6 được chọn chạy lại được ghi rõ nguồn, không đổi tên kết quả cũ thành lượt đo mới.

## Chạy lại

```powershell
python Evidence/tools/validate_w07.py
python verify_week_folders.py
.\.venv\Scripts\python.exe -B tests/run_w7_tests.py
.\.venv\Scripts\python.exe -B tests/smoke_w6_http.py
```

Validator chỉ đọc; test runner ghi runs/w7; HTTP smoke ghi runs/w6, mở loopback server fixture và đọc .env riêng nếu có qua app composition, không xuất credential. Evidence không bị ghi đè khi chạy lại. Không import main hoặc khởi tạo Engine thật.

Quang thực hiện, Đức review qua issue được giao. Không tạo PR mới theo yêu cầu giữ tất cả trên main; issue review không thay thế approval PR nếu giảng viên vẫn yêu cầu PR. Review thực tế đang chờ.

Kết quả chạy ngày 17/11/2026: **28/28 fixture/contract tests đạt**, 0 failures/errors/skips; **2/2 HTTP/SSE fixture cases đạt**. Không model inference/AWS.
