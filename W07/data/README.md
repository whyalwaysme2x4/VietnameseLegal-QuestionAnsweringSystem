# W7 QA development candidates v0.1

30 câu = 10 ngoài phạm vi + 10 thiếu hồ sơ cá nhân giả định + 5 thiếu tình tiết + 5 đối chứng answerable từ 200 QA dev. Trong đó 25 câu synthetic; không chứa dữ liệu người dùng thật. Tập này không phải 30 unanswerable và không phải test độc lập.

## Data dictionary

| Trường | Ý nghĩa |
|---|---|
| id, question | ID W7 ổn định và câu hỏi |
| category, domain | Loại tình huống; domain null nếu ngoài scope |
| expected_action, expected_action_status | answer/clarify/refuse tạm gán, chưa được human review |
| rationale, evidence_status | Lý do và giới hạn chứng cứ |
| supporting_source_ids | Article IDs từ nhãn QA dev đối chứng; không tự dựng gold mới |
| checked_source_ids, absence_marker | 53 document IDs đã tìm marker literal cho ca hồ sơ giả định |
| source_qa_id, reference_answer, source_reference | Chỉ có ở đối chứng, giữ nguyên từ nguồn dev và review pending |
| review_status, split, origin | pending, dev candidate, synthetic hoặc existing_dev_control |
| snapshot_date | 2026-07-01 là mốc tham chiếu, không ngày xác minh hiệu lực |

Không đủ căn cứ cho kết luận cá nhân không đồng nghĩa phải cấm nêu quy định chung có nguồn. Với ca hồ sơ giả định, có thể giải thích giới hạn và đề nghị cung cấp hồ sơ nhưng không được bịa giá trị hồ sơ. Reviewer có thể điều chỉnh nhãn clarify/refuse với lý do trước khi freeze; phải tăng version và giữ lineage.

`corpus_record_check.json` chỉ xác nhận không xuất hiện chính mã giả định trong extracted text 53 DOCX. Chưa rà phủ định ngữ nghĩa mọi quy định; chưa có legal gold. `dataset_card.json` mô tả phân bố và hạn chế. Không gán license mới cho dữ liệu kế thừa; xem ATTRIBUTION.md tại gốc.
