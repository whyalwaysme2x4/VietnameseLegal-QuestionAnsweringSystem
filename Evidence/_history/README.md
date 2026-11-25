# Phiên bản file được dùng bởi evidence lịch sử

Các manifest W01–W07 đã khóa một số đường dẫn ở gốc repo. Khi W8 cập nhật runtime/navigation, các bytes trước đó được sao chép chính xác từ commit nguồn vào đây; index.json ghi week, path, hash và commit. Không sửa manifest/số liệu/trace của tuần cũ để cho khớp code mới.

Validator chỉ dùng snapshot nếu file hiện hành khác hash lịch sử và snapshot khớp đúng hash cũ. W08 manifest vẫn kiểm tra runtime hiện hành, nên việc kiểm tra lịch sử không thay kiểm tra code mới. Các folder W01–W07 theo tuần vẫn nguyên vẹn.
