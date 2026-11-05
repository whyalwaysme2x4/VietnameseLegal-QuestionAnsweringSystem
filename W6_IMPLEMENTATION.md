# W6 — Chuyển agent gốc sang demo

Ngày cập nhật: 05/11/2026. Nội dung kỹ thuật được kiểm tra tại demo local `VietnameseLegalQA-W1-W5`, sau đó đóng gói vào nhánh `main` cùng toàn bộ evidence W01–W06 theo yêu cầu. Thông tin backup local trước migration được ghi trong `Evidence/W06/local-migration-manifest.json`; backup/model/index không đưa vào Git.

## Luồng chạy

`app.py` → `runtime.Engine.chat(mode="agentic")` → `source/agent/demo_agentic.py` → `GraphOrchestrator`.

Planner → multi-query Dense (query gốc + các variants từ generator) → Qdrant top-25/query → RRF top-50 → CrossEncoder top-5 → BERT QA → Grader → chọn vòng tốt nhất → generator nhận full chunk + BERT highlight → Checker → final. Planner/Grader/Checker dùng các class của project gốc; LangGraph chuyển các bước thành node, không thay điều kiện điều khiển.

W3/W4/W5 tiếp tục dùng các chế độ `dense`, `hybrid`, `rerank`, gồm BM25 và cấu hình cũ. W6 `agentic` giữ retrieval gốc multi-query Dense/RRF/CE, không chèn BM25 vào Orchestrator gốc và không sử dụng giới hạn 20 ứng viên của W5. BERT và CrossEncoder W6 được nạp lazily ở lần gọi agentic đầu tiên; model weights đã chuẩn bị trên máy.

## Các hợp đồng được giữ

- `Plan`, `GraderResult`, `CheckResult` và các intent/tool giữ nguyên.
- Planner lỗi parse: fallback `legal/rag`; lỗi provider không được coi là parse fallback.
- Grader lỗi parse: `sufficient`, score `0.6`. Checker lỗi parse: `is_grounded=True`, confidence `0.3`.
- `MAX_ITERATIONS=2` là tổng hai vòng retrieval. Dừng nếu sufficient **hoặc** score ≥ 0.6; giữ vòng có điểm cao nhất, không mặc định lấy vòng cuối.
- Entities từ Planner được dùng cho các query variants và các vòng. Các entity filter vẫn kết hợp `should`/OR; ràng buộc corpus/domain bắt buộc bọc bên ngoài bằng `must`.
- Fallback web ở score < 0.4 và khi không có citation vẫn có trong graph theo logic gốc. Demo gọi với `web_search_enabled=False`, không tự bật web.
- Generator nhận toàn bộ chunk kèm BERT highlight. `key` là **0-based**; giữ nguyên filtering index không hợp lệ và mapping sang references.
- Checker đối chiếu các chunk thực sự được trích dẫn. Chỉ regenerate khi false, confidence ≥ 0.75 và ít nhất hai unsupported claims; sinh lại đúng một lần, không recheck sau đó như code gốc.
- Các điều kiện fail-open ở trên được giữ theo yêu cầu, không có nghĩa nguồn/đáp án đã được kiểm chứng pháp lý.

`source/agent/orchestrator.py`, `grader.py`, `hallucination_checker.py`, extractor/model và các helper gốc được giữ để đối chiếu. Planner chỉ bổ sung giới hạn hai lĩnh vực/53 văn bản và thay ví dụ legal ngoài phạm vi. YAML thêm phạm vi tương ứng; không thay schema citation. Nguồn tái sử dụng được ghi trong `ATTRIBUTION.md`.

## Corpus và model

`source/core/corpus_scope.json` khóa đúng các IDs đã chốt: 38 giao thông (giữ số 36, loại số 8), 15 lao động (loại 3, 6, 10, 12, 14, 20). Snapshot 01/07/2026 vẫn chưa được kiểm chứng hiệu lực đầy đủ.

`index_w6/qdrant` / collection `legalqa_w6_agentic_corpus_v1` là index riêng, không ghi đè index W1–W5. Dùng lại vector sau kiểm tra fingerprint corpus/checkpoint. Payload bổ sung các field legacy `LoaiVanBanFilter`, `NoibanHanhFilter`, `NgayBanHanhFilter` để tương thích filter gốc. Ngày lưu các biểu diễn dd-mm-yyyy/năm; không suy ra ngày hiệu lực.

Checkpoint BERT: `bhuy71/bert_extract_full_fine-tuned`, revision `f36d7cf5299dd91bbee69d90d6ded4a09ad755ce`. Giữ `MAX_LENGTH=512`, `STRIDE=150`, `N_BEST=380`, `MAX_ANSWER_LENGTH=2000` và extraction gốc, không thêm sliding window hoặc sửa thuật toán span. Nova Micro dùng Converse adapter với prompt và token budget của generation gốc. Không dùng credential của project nguồn.

LangGraph 0.4.8 và các dependency tương thích được pin trong `requirements-w6.txt` để giữ LangChain Core 0.3.60 và các model dependency cũ. `requirements-w6-lock.txt` ghi môi trường sau migration; không thay lockfile đã dùng cho số liệu W5.

## Kiểm thử và trace

Chạy `.\.venv\Scripts\python.exe -B tests/run_w6_tests.py` từ thư mục demo trong PowerShell. Có đúng 15 case ở `tests/agent_cases_w6.json`. Mỗi case chạy agent/graph thật và Orchestrator tham chiếu với cùng fixture; đối chiếu các event, vòng lặp, citation và hành vi lỗi. LLM/retrieval/tensor BERT trong suite là fixture để kiểm tra nhánh quyết định một cách xác định.

`Evidence/W06/test-results.json` ghi trạng thái từng case. `Evidence/W06/traces/` là trace LangGraph của **fixture execution**, không phải demo AWS hoặc benchmark model thật. Không dùng chúng để khẳng định độ chính xác phân loại lĩnh vực/đáp án pháp luật.

`tests/smoke_w6_assets.py` kiểm tra riêng assets offline: index scope bằng cached query vector khớp chính xác, một lần extraction BERT thật và nạp CrossEncoder bằng wrapper gốc. `Evidence/W06/asset-smoke.json` phân biệt rõ phần đã chạy và phần chưa chạy. Không gọi AWS hoặc chạy lại 200 QA.

`tests/smoke_w6_http.py` kiểm tra HTTP/SSE qua cổng local tạm thời bằng fixture: final/done, trace đến node finish, citation 0/1, bỏ chỉ số ngoài danh sách và mở nội dung source card. Kết quả ở `Evidence/W06/http-contract-smoke.json`; không gọi AWS hoặc chạy model thật. `Evidence/W06/migration-verification.json` xác nhận 74 file dữ liệu/minh chứng cũ và lockfile baseline không đổi; lớp Planner có AST giống nguồn, chỉ prompt được thu hẹp.

CrossEncoder W6 giữ mặc định wrapper gốc, không áp override 512 token/batch 4 của W5. Khi nạp checkpoint này, `max_length` hiệu dụng là 8192; chưa đo inference/latency CrossEncoder W6. Môi trường hiện tại đã kiểm tra dependency tương thích bằng `uv pip check`.

Trace live của W6 đi qua SSE `graph_node`, `plan`, `grade`, `check`, `iterate`, `extract` và xuất trong phần xem trace sau câu trả lời. Các lời giải thích là lý do quyết định ngắn, không phải chain-of-thought nội bộ. Chỉ trace fixture được lưu tự động; không tạo log mới chứa chat riêng tư.

Chưa xác nhận toàn bộ luồng live với phiên AWS/model hiện tại; 15 test pass không thay live integration test. Kiểm tra thực tế khi chạy demo bằng `Start-Demo.ps1`, chọn W6. Bản này vẫn stateless như demo: session_id=None; không mang SQLite/user facts của project gốc sang.

## Bản đóng gói GitHub

Code hiện hành ở gốc repo, evidence cố định ở `Evidence/W01`–`W06`, cùng nhánh `main`. Các lệnh chạy lại test ghi vào `runs/w6/`; đánh giá mới ghi `runs/evaluation/`, không ghi đè minh chứng đã khóa. `/api/evaluation` ưu tiên lượt chạy local mới, nếu chưa có thì đọc artifact W4/W5 đã lưu. Những khác biệt đường dẫn này được ghi trong `Evidence/W06/packaging.json`.
