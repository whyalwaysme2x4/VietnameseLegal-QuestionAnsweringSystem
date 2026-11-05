# Theo dõi GitHub W01–W06 — cùng main

Cập nhật ngày 05/11/2026 sau khi đối chiếu GitHub. Tất cả code và evidence W01–W06 ở `main`, không cần đổi nhánh. Đỗ Văn Đức (`@dovanduc2004`) phụ trách kiểm tra kết quả/review; collaborator đã được xác nhận. Review W6 đang chờ. Giữ các PR/nhánh cũ làm lịch sử, không tạo nhánh mới cho W6.

| Tuần | Milestone | Thực hiện | Kiểm tra/review | PR | Snapshot |
|---|---|---|---|---|---|
| W01 | [Tuan1](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/3) | [#7](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/7) | [#8](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/8) | [#13](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/13) | [w01](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/tree/w01) |
| W02 | [Tuan2](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/4) | [#9](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/9) | [#10](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/10) | [#14](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/14) | [w02](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/tree/w02) |
| W03 | [Tuan3](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/5) | [#11](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/11) | [#12](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/12) | [#15](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/15) | [w03](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/tree/w03) |
| W04 | [Tuan4](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/1) | [#1](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/1) | [#2](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/2) | [#5](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/5) | [w04](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/tree/w04) |
| W05 | [Tuan5](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/2) | [#3](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/3) | [#4](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/4) | [#6](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/6) | [w05](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/tree/w05) |
| W06 | [Tuan6](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/6) | [#17](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/17) | [#18](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/18) | Cập nhật trực tiếp main | [w06](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/tree/w06) |

## Trạng thái merge/review

PR #13/#14/#15 (W1–W3), #5 (W4) và #6 (W5) đã merge. PR tích hợp #16 đã đưa W5 vào main ngày 01/11/2026, commit `791a910`. API xác nhận APPROVED của Đức ở PR #15/#5/#6; PR #13/#14 không có bản ghi APPROVED riêng. Không coi merge đồng nghĩa với approval.

W6 cập nhật trực tiếp main và gắn tag `w06` theo yêu cầu mới. Không có PR W6, vì vậy **chưa có minh chứng PR/reviewer cho riêng W6** theo form PR gốc của giảng viên. Issue #18 theo dõi review thực tế; Đức có thể nhận xét vào issue/commit. Đây là cách tổ chức được người dùng yêu cầu, không khẳng định thay thế được yêu cầu PR nếu giảng viên vẫn bắt buộc.

Các tag giữ nguyên snapshot đã push; thông tin reviewer cập nhật sau đó nằm trong HEAD của PR và issue. Tag không có nghĩa đã được approval. Kiểm tra tự động thành công không thay review của Đức.

## Kiểm tra số liệu

`python Evidence/tools/validate_evidence.py` chỉ kiểm tra hash và tái tính từ output đã lưu, không chạy model hoặc gọi AWS. W03 dùng subset của lượt đo 31/10/2026; W01/W02 là inventory/corpus validation bổ sung. Nhãn và hiệu lực pháp luật vẫn pending.
