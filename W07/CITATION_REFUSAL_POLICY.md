# W7 — Chính sách trích dẫn và xử lý thiếu căn cứ

Tuần kế hoạch 08/11–14/11/2026. Tài liệu đóng gói sau tuần kế hoạch, ngày 17/11/2026; không backdate triển khai hay kiểm thử. Phạm vi: 53 DOCX, hai lĩnh vực Giao thông vận tải và Lao động tiền lương; mốc tham chiếu 01/07/2026 chưa chứng minh hiệu lực từng văn bản.

## Quy tắc đang có trong code

| Thành phần | Hợp đồng hiện hành | Bằng chứng từ gốc repo |
|---|---|---|
| Agent Generator | JSON `answer`, `key`; key 0-based trong danh sách chunk; lọc chỉ số ngoài phạm vi khi dựng references | `source/agent/orchestrator.py::_generate_rag_answer` |
| Mapping UI agent | Chọn source theo citation_indices và selected_chunk_ids; không cộng/trừ để chuyển thành hợp đồng baseline | `source/agent/demo_agentic.py` |
| Baseline Generator | `answer`, `citations`; parser 1-based, kiểm tra schema/chỉ số; phản hồi hỏng không được gán nguồn chắc chắn | `source/generate/synthesis_response.py`, `tests/test_synthesis_response.py` |
| Nguồn | Chunk và metadata: số hiệu, cơ quan, ngày ban hành, điều và nội dung | Orchestrator, `runtime.Engine.source`, `app.js` |
| Nội dung generation | Toàn bộ chunk được chọn kèm BERT highlight, không chỉ một BERT span | `_build_generator_input` |

Chỉ số hợp lệ không chứng minh nguồn hỗ trợ mọi claim. Code agent chưa có kiểm tra kiểu citation chặt cho mọi giá trị đầu ra; không mô tả nó ngang parser baseline. Reference không đồng nghĩa nguồn chính thức hay luật còn hiệu lực. Nội dung UI có thể là node Điều/Khoản liên quan, không mặc nhiên toàn bộ DOCX.

## Ma trận xử lý và giới hạn

| Tình huống | Behavior hiện tại | Mục tiêu đánh giá W7, chưa cam kết đã đạt |
|---|---|---|
| Ngoài phạm vi | Planner có reject; fixture kiểm tra routing khi nhãn đã được cung cấp | Từ chối lịch sự, không bịa căn cứ ngoài hai lĩnh vực |
| Thiếu tình tiết | Có tool ask_user/nhánh clarify | Hỏi dữ kiện cần thiết trước khi kết luận cá nhân |
| Không có references sau generation | Web bật có thể fallback; web tắt trả thông báo thiếu cơ sở tri thức | Không xuất câu trả lời nội dung thiếu căn cứ như thành công |
| Grader score thấp | Tổng hai vòng retrieval, giữ vòng tốt nhất; <0,4 chỉ kích hoạt web fallback nếu web bật | Không coi điểm thấp là điều kiện hard-refusal đang có |
| Lỗi provider | SSE error/lượt xử lý lỗi | Ghi lỗi riêng; không tính là từ chối đúng |
| Lỗi parse Grader | sufficient, score 0,6 | Ghi nhận fail-open, không coi đó là xác nhận đủ nguồn |
| Lỗi parse Checker | grounded=true, confidence 0,3 | Ghi nhận checker_error/fallback khi rà trace |

Demo stateless, web tắt. Thông báo không nguồn kế thừa vẫn gợi ý bật Web Search; UI hiện không cung cấp đầy đủ luồng này. Giữ nguyên chính sách gốc, ghi rõ bất nhất thay vì thay behavior trong nhiệm vụ đóng gói evidence.

## Checker và sinh lại

Checker chỉ đối chiếu nguồn đã được dẫn: `source/agent/hallucination_checker.py`, `graph_orchestrator.py::_check_node`. Mỗi nguồn bị giới hạn 1.500 ký tự; đáp án 4.000 ký tự. Kết quả gồm is_grounded, confidence, unsupported_claims và reason. Confidence chưa được hiệu chỉnh thành xác suất đúng.

Chỉ sinh lại khi đồng thời grounded=false, confidence ≥0,75 và có ít nhất hai unsupported claims. Sinh lại tối đa một lần, dùng full chunk+BERT; không recheck sau sinh lại, không có gate citation lần hai trong đường này. Một lỗi đơn lẻ có thể không kích hoạt sửa. Checker fail-open hoặc câu trả lời trống được đánh dấu grounded trong helper không được đưa thẳng thành điểm chất lượng tốt.

Đây là mô tả code hiện hành, không phải chứng nhận tính đúng pháp lý. Không đổi ngưỡng, số vòng, policy lỗi hoặc mapping nguồn trong W7 packaging.
