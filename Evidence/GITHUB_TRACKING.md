# Theo dõi GitHub W01–W05

Tổ chức và cập nhật ngày 01/11/2026. Đỗ Văn Đức (`@dovanduc2004`) phụ trách kiểm tra kết quả/review. Trạng thái truy cập: `collaborator_confirmed`. Review thực tế vẫn chưa hoàn tất.

| Tuần | Milestone | Thực hiện | Kiểm tra/review | PR | Snapshot |
|---|---|---|---|---|---|
| W01 | [Tuan1](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/3) | [#7](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/7) | [#8](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/8) | [#13](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/13) | [w01](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/tree/w01) |
| W02 | [Tuan2](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/4) | [#9](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/9) | [#10](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/10) | [#14](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/14) | [w02](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/tree/w02) |
| W03 | [Tuan3](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/5) | [#11](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/11) | [#12](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/12) | [#15](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/15) | [w03](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/tree/w03) |
| W04 | [Tuan4](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/1) | [#1](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/1) | [#2](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/2) | [#5](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/5) | [w04](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/tree/w04) |
| W05 | [Tuan5](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/milestone/2) | [#3](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/3) | [#4](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/issues/4) | [#6](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/pull/6) | [w05](https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem/tree/w05) |

## Trình tự review/merge

PR #5 chứa nền evidence dùng chung và W4, chưa merge. Các PR W01–W03 bổ sung liên kết/quản lý từng tuần, dùng base `evidence/w04` và chỉ sửa file tuần tương ứng. PR #6 (W5) cũng dựa trên nền W4. Review/merge PR #5 trước, sau đó retarget các PR còn lại về main. Không đổi lịch sử hoặc tạo PR rỗng để giả lập phát triển theo thứ tự thời gian.

Các tag giữ nguyên snapshot đã push; thông tin reviewer cập nhật sau đó nằm trong HEAD của PR và issue. Tag không có nghĩa đã được approval. Kiểm tra tự động thành công không thay review của Đức.

## Kiểm tra số liệu

`python Evidence/tools/validate_evidence.py` chỉ kiểm tra hash và tái tính từ output đã lưu, không chạy model hoặc gọi AWS. W03 dùng subset của lượt đo 31/10/2026; W01/W02 là inventory/corpus validation bổ sung. Nhãn và hiệu lực pháp luật vẫn pending.
