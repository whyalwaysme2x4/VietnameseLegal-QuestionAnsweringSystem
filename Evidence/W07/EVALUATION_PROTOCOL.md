# W7 — Evaluation protocol có thể kiểm tra lại

## Câu hỏi đánh giá

- RQ1: Citation có ánh xạ đúng nguồn và claim có được chính nguồn được dẫn hỗ trợ không?
- RQ2: Hệ thống phân biệt answer/clarify/refuse thế nào trên QA phát triển, và có từ chối nhầm câu có căn cứ không?
- RQ3: Các nhánh Checker, parse fallback, sinh lại và lỗi dịch vụ có tuân thủ chính sách code gốc không?

RQ3 được kiểm tra bằng fixture tái lập. RQ1 về ngữ nghĩa và RQ2 trên LLM thật chưa có kết quả. Không dùng Recall@k hay 100% fixture pass làm đáp án cho RQ1/RQ2.

## Dữ liệu và đóng băng

`data/qa_candidates_30.jsonl`: 25 câu synthetic (10 ngoài scope, 10 hồ sơ cá nhân giả định không được cung cấp, 5 thiếu tình tiết) + 5 đối chứng lấy nguyên từ 200 QA dev. Các hành động kỳ vọng provisional; human/legal review pending. Đây là dev candidate, không phải final test độc lập và không phải 30 câu đều unanswerable. Không có hồ sơ/người dùng thật.

10 mã hồ sơ giả định được tìm literal trong 53 văn bản đã trích text. `corpus_record_check.json` ghi số văn bản và kết quả. Không có mã không chứng minh thiếu mọi đáp án pháp luật theo nghĩa ngữ nghĩa. Reviewer cần rà câu hỏi, hành động và nguồn; đặc biệt đối chứng vẫn có nhãn cũ chưa kiểm chứng. Chưa có gold hoặc ngày đóng băng final test được xác nhận. Dùng tập này chỉnh hệ thống thì không dùng lại như test độc lập.

## Lặp lại các kiểm tra đã tự động hóa

Từ gốc repo:

```powershell
python Evidence/tools/validate_w07.py
python verify_week_folders.py
# Môi trường đầy đủ theo requirements-w6-lock.txt, không cần AWS/model weights:
.\.venv\Scripts\python.exe -B tests/run_w7_tests.py
# Smoke HTTP/SSE fixture, chỉ mở server loopback tạm thời:
.\.venv\Scripts\python.exe -B tests/smoke_w6_http.py
```

Test W7 chọn 10 case liên quan từ W6 (citation, reject, empty sources, fail-open, regeneration, provider error), 11 test synthesis baseline và kiểm tra contract/dataset W7. Đây là thực thi lại code bằng fixture trong W7, không tái gọi model thật; trace có fixture_execution=true. Runner ghi `runs/w7`, smoke hiện ghi `runs/w6`; không ghi đè Evidence đã khóa. Validator dùng stdlib chỉ kiểm tra dữ liệu, hash và kết quả lưu. Source UI kiểm tra contract HTML/JS và API bằng fixture, chưa kiểm thử trực quan browser/accessibility.

## Chạy QA với mô hình thật: quy trình cần thực hiện

1. Reviewer hoàn tất nhãn và phân biệt corpus-missing với retrieval-miss; khóa hash corpus/index, QA, code, model revisions, prompt và cấu hình chạy.
2. Chạy demo từ gốc repo, mode agentic, domain all, web tắt, câu hỏi độc lập. Gửi từng câu qua POST /api/chat với payload `{question, domain: "all", mode: "agentic"}`; giữ toàn bộ SSE liên quan và final. Bước này gọi Bedrock và cần cấu hình riêng; chưa thực hiện trong evidence này. Không bịa CLI batch runner đã tồn tại.
3. Lưu mỗi QA theo `annotation_template.json`: run_id, answer, observed_action, pipeline_status, candidates/citations/checker/latency. Nếu event không xuất parse-fallback riêng, cần rà trace/đầu ra để đánh dấu; không tự coi fallback là checker thành công.
4. Rà claim thực chất và nguồn trích dẫn; nhận xét supported/unsupported/uncertain, trích đoạn nguồn; kiểm tra citation hợp lệ bằng ID. Quang và Đức rà, giải quyết bất đồng và lưu tên reviewer/thời điểm thực tế; chưa tuyên bố đã review.
5. Tổng hợp đúng mẫu số; giữ lỗi trong inventory, báo riêng tỷ lệ lỗi/coverage. Chưa có script tính semantic grounding tự động trong W7; metric runner thật cần được bổ sung sau khi có predictions/annotations.

## Định nghĩa metrics (chưa đo chất lượng LLM)

| Metric | Định nghĩa | Điều kiện |
|---|---|---|
| Citation validity | Liên kết citation ánh xạ được đúng nguồn / tổng citation được kiểm tra | 0-based agent, 1-based baseline; không gộp lệch offset |
| Grounding support | Claim được nguồn trích dẫn hỗ trợ / tổng claim thực chất đã rà | uncertain vẫn trong mẫu số, không tính supported; báo số uncertain riêng |
| Refusal recall | QA nhãn refuse được xử lý refuse đúng / tổng QA nhãn refuse | Lỗi dịch vụ vẫn nằm mẫu số, không là true positive |
| False refusal rate | QA nhãn answer bị refuse / tổng QA nhãn answer | Báo riêng errors/coverage để tỷ lệ thấp do lỗi không bị hiểu tốt |
| Clarification accuracy | QA nhãn clarify được hỏi lại phù hợp / tổng QA nhãn clarify | Không tính generic error là clarify |
| Pipeline error rate | QA bị lỗi provider/pipeline / tổng QA đã gửi | Ghi cả loại lỗi, không bỏ mẫu |

Mẫu số 0: N/A, không gán 0 hoặc 100%. Không có citation ở lượt từ chối đúng không phải citation-validity=100%. Câu answer không citation cần ghi riêng citation coverage. Grounding support phải báo số QA không sinh claim và số lỗi để tránh thiên lệch do bỏ đáp án rỗng. Chỉ số Checker khác nhãn chấm độc lập.

`metrics.csv` tách inventory/fixture thực đo và semantic metrics `not_measured`. Không có kết quả Nova/hiệu lực pháp lý/independent test trong gói này. Không chạy hoặc đề xuất ablation đổi policy trong nhiệm vụ này.
