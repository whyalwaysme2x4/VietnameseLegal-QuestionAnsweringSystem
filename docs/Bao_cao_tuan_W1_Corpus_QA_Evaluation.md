# BÁO CÁO TIẾN ĐỘ TUẦN 1

### Thông tin chung

Tuần: W1

Thời gian: 27/09–03/10/2026

Tên đề tài: ______________________________

Nhóm: ______________________________

Thành viên: ______________________________

GitHub repository: https://github.com/whyalwaysme2x4/VietnameseLegal-QuestionAnsweringSystem.git

## 1. Tóm tắt tiến độ

Trong tuần W1, nhóm tập trung hoàn thiện các công việc nền tảng cho hệ thống hỏi đáp pháp luật tiếng Việt, bao gồm:

- Chốt phạm vi pháp luật của hệ thống.
- Xác định nguồn văn bản pháp luật sử dụng để xây dựng corpus.
- Chốt snapshot date làm mốc tham chiếu pháp lý.
- Xây dựng Corpus Plan.
- Xây dựng bộ 50 câu hỏi – đáp án pilot phục vụ đánh giá.
- Xây dựng Evaluation Protocol cho hệ thống.
- Xác định các nguyên tắc đạo đức, phạm vi sử dụng và giới hạn của hệ thống.
- Tổ chức repository phục vụ quản lý mã nguồn, tài liệu và dữ liệu của đồ án.

Corpus hiện tại gồm 53 văn bản, thuộc hai lĩnh vực Giao thông vận tải và Lao động – tiền lương. Bộ đánh giá ban đầu gồm 50 câu hỏi QA pilot, được chia đều cho hai lĩnh vực.

Trong tuần W1, nhóm chưa thực hiện chạy benchmark chính thức trên mô hình, do đó báo cáo tập trung vào việc chuẩn bị dữ liệu và thiết kế quy trình đánh giá, chưa đưa ra các điểm số thực nghiệm của hệ thống.

## 2. Phạm vi pháp luật

Hệ thống được giới hạn trong hai lĩnh vực pháp luật:

1. Giao thông vận tải
2. Lao động – tiền lương

Việc giới hạn phạm vi giúp corpus có tính tập trung, đồng thời tạo điều kiện để nhóm kiểm soát tốt hơn nguồn văn bản và căn cứ pháp lý được sử dụng trong quá trình truy xuất và sinh câu trả lời.

Ở giai đoạn W1, corpus gồm tổng cộng 53 văn bản, trong đó:

- 38 văn bản thuộc lĩnh vực Giao thông vận tải.
- 15 văn bản thuộc lĩnh vực Lao động – tiền lương.

Các câu hỏi nằm ngoài hai lĩnh vực trên không thuộc phạm vi xử lý chính thức của hệ thống trong phiên bản hiện tại.

## 3. Nguồn dữ liệu

### 3.1. Nguồn văn bản pháp luật

Nguồn dữ liệu của corpus được xác định dựa trên các nguồn công bố pháp luật chính thức hoặc có thẩm quyền, thay vì coi các bản sao nội bộ trong repository là nguồn gốc của văn bản.

Các nguồn được ưu tiên gồm:

- Cơ sở dữ liệu quốc gia về văn bản pháp luật.
- Công báo điện tử.
- Cổng thông tin điện tử của cơ quan ban hành văn bản.
- Các hệ thống công bố văn bản chính thức khác của cơ quan nhà nước có thẩm quyền, khi cần đối chiếu.

Các nguồn trên được sử dụng để phục vụ việc xác định nội dung văn bản, căn cứ pháp lý và đối chiếu thông tin của corpus.

Trong các giai đoạn tiếp theo, từng văn bản trong corpus sẽ được truy vết cụ thể tới nguồn công bố chính thức tương ứng.

### 3.2. Nguồn câu hỏi đánh giá

Bộ QA pilot gồm 50 câu hỏi, được lựa chọn từ tập câu hỏi hiện có của dự án và chia thành:

- 25 câu thuộc lĩnh vực Giao thông vận tải.
- 25 câu thuộc lĩnh vực Lao động – tiền lương.

Câu hỏi được giữ theo nội dung dữ liệu gốc. Đáp án tham chiếu ban đầu được xây dựng dựa trên các điều khoản pháp luật thuộc corpus.

Các đáp án này được sử dụng cho giai đoạn pilot và sẽ tiếp tục được kiểm chứng trước khi khóa thành bộ gold benchmark chính thức.

## 4. Snapshot date

Snapshot date của corpus được chốt là ngày 01/07/2026.

Snapshot date được hiểu là mốc thời gian pháp lý mà hệ thống sử dụng khi xác định nội dung pháp luật áp dụng và khi đánh giá câu trả lời.

Ví dụ, khi một câu hỏi được đưa vào benchmark, câu trả lời chuẩn cần được xem xét theo trạng thái pháp luật tại thời điểm 01/07/2026, thay vì tự động áp dụng các thay đổi pháp luật phát sinh sau mốc này.

Snapshot date không đồng nghĩa với:

- ngày tải tài liệu;
- ngày truy cập trang web;
- ngày tạo dataset;
- hoặc ngày nộp báo cáo.

Việc xác minh chi tiết trạng thái hiệu lực của từng văn bản, ngày truy cập nguồn, quan hệ sửa đổi, thay thế và các metadata liên quan sẽ được thực hiện ở giai đoạn tiếp theo.

## 5. Corpus Plan

Corpus của hệ thống được xây dựng nhằm cung cấp nguồn căn cứ cho quá trình retrieval và sinh câu trả lời pháp luật.

Corpus W1 hiện gồm 53 văn bản, chia thành hai nhóm:

| Lĩnh vực | Số lượng |
| --- | --- |
| Giao thông vận tải | 38 |
| Lao động – tiền lương | 15 |
| Tổng cộng | 53 |

### 5.1. Mục tiêu của corpus

Corpus được xây dựng nhằm:

- Cung cấp nguồn văn bản cho hệ thống retrieval.
- Cho phép hệ thống truy xuất các điều khoản có liên quan đến câu hỏi.
- Cung cấp căn cứ cho câu trả lời của mô hình.
- Hỗ trợ kiểm tra khả năng grounding của hệ thống.
- Phục vụ xây dựng và đánh giá bộ QA benchmark.

### 5.2. Nguyên tắc xây dựng corpus

Các văn bản được lựa chọn cần:

- Thuộc một trong hai lĩnh vực đã chốt.
- Có liên quan trực tiếp đến các nhóm câu hỏi mà hệ thống dự kiến xử lý.
- Có khả năng truy vết về nguồn công bố pháp luật chính thức.
- Giữ được cấu trúc pháp lý quan trọng như Điều, Khoản, Điểm để phục vụ retrieval và citation.
- Không sử dụng các đoạn không xác định được căn cứ làm nguồn cho đáp án chuẩn.

Trong W1, nhóm tập trung vào việc xác định tập văn bản và cấu trúc corpus.

Các công việc như xây dựng manifest hoàn chỉnh, chuẩn hóa metadata, hash tệp, trạng thái hiệu lực và quan hệ sửa đổi giữa các văn bản được chuyển sang giai đoạn tiếp theo.

## 6. Bộ QA Pilot

Trong tuần W1, nhóm xây dựng bộ 50 câu hỏi – đáp án pilot nhằm phục vụ việc kiểm tra ban đầu và thiết kế quy trình đánh giá cho hệ thống hỏi đáp pháp luật.

Bộ QA được chia đều theo hai lĩnh vực:

- 25 câu thuộc lĩnh vực Giao thông vận tải.
- 25 câu thuộc lĩnh vực Lao động – tiền lương.

Các câu hỏi được lựa chọn từ tập câu hỏi hiện có của dự án. Nội dung câu hỏi được giữ theo dữ liệu gốc. Với mỗi câu hỏi, nhóm xây dựng đáp án tham chiếu dựa trên các văn bản thuộc corpus và xác định điều khoản pháp lý tương ứng.

Bộ QA pilot được sử dụng để:

1. Kiểm tra khả năng hệ thống truy xuất đúng văn bản và điều khoản liên quan.
2. Kiểm tra chất lượng câu trả lời dựa trên nguồn pháp luật.
3. Thiết kế các tiêu chí và chỉ số trong Evaluation Protocol.
4. Phát hiện các trường hợp retrieval sai, dẫn sai căn cứ hoặc sinh thông tin vượt quá nội dung nguồn.

Ở W1, đây là bộ pilot phục vụ thiết kế và thử nghiệm ban đầu, chưa được xem là gold benchmark chính thức. Các đáp án dưới đây là đáp án tham chiếu và sẽ tiếp tục được kiểm chứng về hiệu lực văn bản, điều kiện áp dụng và quan hệ sửa đổi trước khi khóa benchmark chính thức.

### 6.1. QA Pilot – Giao thông vận tải

#### GT01

**Câu hỏi:**
Anh B huyện X muốn biết khi tôi lái xe ô tô đi trên đường mà không chấp hành hiệu lệnh, chỉ dẫn của biển báo hiệu, vạch kẻ đường thì bị XPVP như thế nào?

**Đáp án tham chiếu:**
Người lái ô tô không chấp hành biển báo hoặc vạch kẻ đường thuộc trường hợp phạt 400.000–600.000 đồng, nếu hành vi không rơi vào điều khoản xử phạt riêng được liệt kê tại chính điểm này.

*Căn cứ: Điều 6 khoản 1 điểm a của văn bản tương ứng trong corpus.*

#### GT02

**Câu hỏi:**
Chị H ngồi trên xe ô tô không thắt dây an toàn khi xe đang chạy có bị xử phạt vi phạm không? Nếu bị phạt thì chị bị xử phạt với mức phạt là bao nhiêu?

**Đáp án tham chiếu:**
Người được chở trên ô tô không thắt dây đai an toàn tại vị trí có trang bị dây khi xe đang chạy bị phạt 350.000–400.000 đồng.

*Căn cứ: Điều 12 khoản 4 của văn bản tương ứng trong corpus.*

#### GT03

**Câu hỏi:**
Chị V đi xe máy trên đường chở theo 2 người lớn thì bị xử phạt bao nhiêu?

**Đáp án tham chiếu:**
Xe mô tô hai bánh, xe gắn máy thông thường chỉ được chở một người. Chở thêm hai người lớn ngoài các ngoại lệ luật định bị phạt 400.000–600.000 đồng.

*Căn cứ: Điều 33 khoản 1 và Điều 7 khoản 2 điểm g của các văn bản tương ứng trong corpus.*

#### GT04

**Câu hỏi:**
Anh V hỏi theo quy định hành vi đi xe máy không đội mũ bảo hiểm bị xử phạt như thế nào?

**Đáp án tham chiếu:**
Người lái xe máy phải đội mũ đạt quy chuẩn và cài quai đúng cách; vi phạm bị phạt 400.000–600.000 đồng.

*Căn cứ: Điều 33 khoản 2 và Điều 7 khoản 2 điểm h.*

#### GT05

**Câu hỏi:**
Chị B hỏi người đi bộ tham gia giao thông bị xử phạt trong trường hợp nào?

**Đáp án tham chiếu:**
Người đi bộ phải đi đúng phần đường và qua đường đúng nơi, theo tín hiệu. Các lỗi thông thường tại khoản 1 bị phạt 150.000–250.000 đồng; đi vào cao tốc hoặc mang vật cồng kềnh gây cản trở thuộc khoản 2, phạt 400.000–600.000 đồng.

*Căn cứ: Điều 30 khoản 1 và Điều 10 của các văn bản tương ứng trong corpus.*

#### GT06

**Câu hỏi:**
Người điều khiển xe mô tô hai bánh, xe gắn máy phải tuân theo những quy tắc gì khi tham gia giao thông?

**Đáp án tham chiếu:**
Người lái mô tô, xe gắn máy chỉ chở một người, trừ ngoại lệ được chở tối đa hai người; người đi xe phải đội mũ đúng quy cách; không sử dụng ô, buông hai tay, chở vật cồng kềnh hoặc thực hiện hành vi gây mất an toàn.

*Căn cứ: Điều 33 khoản 1–4.*

#### GT07

**Câu hỏi:**
Cài mũ bảo hiểm như thế nào thì đúng quy cách?

**Đáp án tham chiếu:**
Mũ bảo hiểm phải đáp ứng quy chuẩn kỹ thuật quốc gia và được cài quai đúng quy cách khi tham gia giao thông.

*Căn cứ: Điều 33 khoản 2.*

#### GT08

**Câu hỏi:**
Khi tham gia giao thông, người đi bộ phải thực hiện quy tắc giao thông nào?

**Đáp án tham chiếu:**
Người đi bộ đi trên vỉa hè, lề đường hoặc đường riêng; nếu không có thì đi sát mép phải. Qua đường tại nơi có tín hiệu, vạch, cầu vượt hoặc hầm; nơi không có các vị trí đó phải quan sát, bảo đảm an toàn và ra tín hiệu bằng tay.

*Căn cứ: Điều 30 khoản 1.*

#### GT09

**Câu hỏi:**
Khi đi trên đường, nếu gặp các loại xe cồng kềnh như xe công nông đang chở đầy hàng, một chiếc máy kéo, xe thồ… Nếu muốn vượt thì phải làm thế nào?

**Đáp án tham chiếu:**
Khi vượt, thông thường phải vượt bên trái và chỉ thực hiện khi đủ điều kiện an toàn. Xe phía trước phải tạo điều kiện cho vượt khi an toàn; nếu không đủ điều kiện thì báo hiệu để xe sau biết.

*Căn cứ: Điều 14 khoản 2–4.*

#### GT10

**Câu hỏi:**
Anh A đang điều khiển xe gắn máy đi trên đường. Đến đoạn đường giao cắt với ngõ nhỏ thì bị anh B điều khiển xe gắn máy khác đi từ ngõ ra đâm vào, xảy ra tai nạn. Trách nhiệm thuộc về ai?

**Đáp án tham chiếu:**
Nếu anh B đi từ đường nhánh hoặc đường không ưu tiên ra đường chính thì phải nhường xe đang đi trên đường chính từ mọi hướng. Kết luận lỗi cụ thể còn phụ thuộc biển báo và chứng cứ hiện trường.

*Căn cứ: Điều 22 khoản 1.*

#### GT11

**Câu hỏi:**
Điều khiển xe máy ở những đoạn dốc lên nguy hiểm, cần giữ khoảng cách với các phương tiện đi trước cùng chiều như thế nào?

**Đáp án tham chiếu:**
Người lái phải giữ khoảng cách an toàn tối thiểu với xe trước và điều chỉnh tốc độ theo địa hình, tầm nhìn, thời tiết; ở dốc nguy hiểm cần giảm tốc hoặc dừng khi cần để bảo đảm an toàn.

*Căn cứ: Điều 12 khoản 1–3.*

#### GT12

**Câu hỏi:**
Khi điều khiển phương tiện giao thông đến chỗ giao nhau với đường sắt không có đèn tín hiệu, rào chắn và chuông báo hiệu, người điều khiển phương tiện giao thông nên xử lý thế nào? Trong trường hợp này, người điều khiển phương tiện giao thông đường bộ phải đứng cách xa đường ray bao nhiêu mét?

**Đáp án tham chiếu:**
Tại đường ngang không có người gác, chắn, chuông hay đèn, người lái dừng bên phải trước vạch dừng, quan sát hai phía và chỉ đi khi không có tàu. Điều khoản này không ấn định một khoảng cách mét chung thay cho vạch dừng.

*Căn cứ: Điều 24 khoản 2.*

#### GT13

**Câu hỏi:**
Thời gian gần đây, trên đường phố nơi tôi sinh sống, mỗi buổi sáng, người dân tụ tập trên hè phố rất đông để họp chợ, mua bán hàng. Thậm chí một số người còn đặt biển hiệu, bàn ghế trên hè phố gây cản trở cho người đi bộ. Khi được tổ trưởng tổ dân phố nhắc nhở thì những người dân đó phản hồi rằng: hè phố là nơi thích hợp để buôn bán; nếu như việc buôn bán không lấn xuống lòng đường, không ảnh hưởng đến xe cộ đi lại thì không phải là vi phạm pháp luật. Xin hỏi ý kiến này có chính xác không?

**Đáp án tham chiếu:**
Sử dụng trái phép lòng đường, vỉa hè để họp chợ, kinh doanh ăn uống, bày bán hàng hóa có thể bị phạt 2–3 triệu đồng với cá nhân hoặc 4–6 triệu đồng với tổ chức.

*Căn cứ: Điều 12 khoản 7.*

#### GT14

**Câu hỏi:**
Cuối tháng 6, khi đang lưu thông trên đường tôi gặp anh M đi xe máy, phía sau chở hàng hóa rất cồng kềnh. Chiều rộng của khối hàng hóa vượt quá bề rộng của giá đèo hàng là 0,5 m; chiều dài vượt quá đuôi xe 1 m. Do khối hàng hóa rất to và nặng, ảnh hưởng đến việc lái xe nên anh M đã va chạm vào xe máy của tôi. Cho rằng anh M đã vi phạm pháp luật nên tôi yêu cầu bồi thường. Tuy nhiên, anh ta đã giải thích rằng việc xếp hàng hóa đó là đúng theo kích thước mà pháp luật quy định.

**Đáp án tham chiếu:**
Hàng trên mô tô, xe gắn máy không được vượt quá mỗi bên giá đèo hàng 0,3 m, vượt sau giá đèo hàng 0,5 m; chiều cao từ mặt đường không vượt quá 2 m. Yêu cầu bồi thường do va chạm phải được đánh giá riêng theo tình tiết và pháp luật dân sự.

*Căn cứ: Điều 33 khoản 5.*

#### GT15

**Câu hỏi:**
Anh K điều khiển xe ô tô đang lưu thông trên đường quốc lộ. Quan sát phía trước an toàn và có đủ điều kiện vượt, anh K báo hiệu để xin vượt. Tuy nhiên xe ô tô phía trước không nhường đường. Nhận thấy rằng không có chướng ngại vật bên phải nên anh K đã đánh xe về phía bên phải làn đường và vượt lên. Hỏi trong tình huống này, anh K hay lái xe phía trước đã vi phạm quy định của Luật an toàn giao thông đường bộ?

**Đáp án tham chiếu:**
Xe xin vượt chỉ được vượt phải trong các ngoại lệ luật định; không thể mặc nhiên vượt phải vì xe trước chưa nhường. Xe trước cũng phải tạo điều kiện cho vượt nếu đủ an toàn, không được cản trở.

*Căn cứ: Điều 14 khoản 2–4.*

#### GT16

**Câu hỏi:**
Trách nhiệm của công dân khi xảy ra tai nạn giao thông đường bộ được quy định như thế nào? Hành vi không cứu giúp người bị tai nạn giao thông có thể bị xử lý như thế nào?

**Đáp án tham chiếu:**
Người gây tai nạn, người liên quan và người chứng kiến phải thực hiện trách nhiệm bảo vệ hiện trường, cứu giúp và báo tin theo quy định. Người có điều kiện mà cố ý không cứu giúp nạn nhân bị phạt 500.000–1.000.000 đồng nếu là cá nhân.

*Căn cứ: Điều 80 và Điều 12 khoản 6 điểm a.*

#### GT17

**Câu hỏi:**
Hiệu lệnh của người điều khiển giao thông và tín hiệu đèn giao thông đường bộ được quy định như thế nào? Trong trường hợp hiệu lệnh của người điều khiển giao thông mâu thuẫn với tín hiệu đèn giao thông thì phải chấp hành như thế nào?

**Đáp án tham chiếu:**
Thứ tự ưu tiên là hiệu lệnh người điều khiển giao thông, đèn tín hiệu, biển báo, vạch kẻ đường rồi các dấu hiệu khác. Khi hiệu lệnh cảnh sát giao thông khác đèn tín hiệu, phải theo hiệu lệnh của người điều khiển giao thông.

*Căn cứ: Điều 11 khoản 1–3.*

#### GT18

**Câu hỏi:**
Anh C thường xuyên lái xe máy có đội mũ bảo hiểm nhưng cài quai ra phía sau gáy. Một lần, anh bị cảnh sát giao thông phát hiện và yêu cầu anh nộp phạt về hành vi này. Tuy nhiên, anh C cho rằng việc đội mũ bảo hiểm của mình như thế là không vi phạm pháp luật, anh C không đồng ý với quyết định xử phạt của cảnh sát giao thông. Xin hỏi hành vi cài quai mũ bảo hiểm ra phía sau gáy có phải là vi phạm pháp luật không?

**Đáp án tham chiếu:**
Cài quai mũ ra sau gáy không đáp ứng yêu cầu cài quai đúng quy cách. Người lái xe máy có thể bị phạt 400.000–600.000 đồng.

*Căn cứ: Điều 33 khoản 2 và Điều 7 khoản 2 điểm h.*

#### GT19

**Câu hỏi:**
Theo quy định của pháp luật, hoạt động giao thông đường bộ phải bảo đảm những nguyên tắc nào?

**Đáp án tham chiếu:**
Hoạt động giao thông phải tuân thủ pháp luật, bảo đảm trật tự, an toàn, thông suốt; mọi cá nhân, tổ chức có trách nhiệm giữ an toàn cho mình và người khác, vi phạm phải được phát hiện và xử lý theo pháp luật.

*Căn cứ: Điều 3.*

#### GT20

**Câu hỏi:**
Khi muốn dừng xe, đỗ xe, để bảo đảm an toàn giao thông, người điều khiển phương tiện tham gia giao thông phải tuân thủ những quy tắc nào?

**Đáp án tham chiếu:**
Khi dừng, đỗ xe phải báo hiệu khi ra vào vị trí, bảo đảm không cản trở người đi bộ và phương tiện khác, sử dụng phanh đỗ hoặc biện pháp an toàn; không dừng đỗ tại các vị trí cấm theo quy định.

*Căn cứ: Điều 18 khoản 1–4.*

#### GT21

**Câu hỏi:**
Khi tham gia giao thông trên đường cao tốc, người điều khiển phương tiện tham gia giao thông phải tuân thủ những quy tắc nào?

**Đáp án tham chiếu:**
Khi vào cao tốc phải báo hiệu, nhường xe đang chạy và nhập làn an toàn; khi ra phải chuyển dần sang làn phải. Không đi trên làn dừng khẩn cấp; chỉ dừng đúng nơi, trừ sự cố và phải cảnh báo theo luật.

*Căn cứ: Điều 25 khoản 1–3.*

#### GT22

**Câu hỏi:**
Nhân dịp sinh nhật lần thứ 19 và để chúc mừng thi đỗ đại học, chị Thúy được bố mua tặng một chiếc xe máy Atila có dung tích xi lanh là 111 cm³ để đi học. Trong trường hợp này, để được tham gia giao thông an toàn đúng quy định của pháp luật thì chị Thúy cần phải đáp ứng những điều kiện gì?

**Đáp án tham chiếu:**
Người 19 tuổi đủ tuổi được cấp giấy phép lái xe hạng A1 cho xe mô tô hai bánh 111 cm³; cần có giấy phép phù hợp còn hiệu lực, còn điểm, đủ sức khỏe và mang giấy tờ theo quy định.

*Căn cứ: Điều 56 khoản 1; Điều 57 khoản 1 điểm a; Điều 59 khoản 1 điểm b.*

#### GT23

**Câu hỏi:**
Ông Đ là chủ một doanh nghiệp sản xuất bánh kẹo nhỏ. Do làm ăn có lãi nên ông Đ mua một chiếc xe ô tô để tiện việc đi lại và phục vụ cho hoạt động kinh doanh. Để ông Đ có thể sử dụng chiếc xe ô tô này tham gia giao thông thì chiếc xe phải đáp ứng các điều kiện nào?

**Đáp án tham chiếu:**
Ô tô tham gia giao thông phải có đăng ký và biển số, bảo đảm an toàn kỹ thuật, môi trường và được kiểm định theo quy định. Xe kinh doanh vận tải còn phải đáp ứng yêu cầu thiết bị giám sát tương ứng.

*Căn cứ: Điều 35 khoản 1–2; Điều 42 khoản 1.*

#### GT24

**Câu hỏi:**
Người điều khiển xe máy chuyên dùng tham gia giao thông phải đáp ứng các điều kiện nào?

**Đáp án tham chiếu:**
Người điều khiển xe máy chuyên dùng phải đủ tuổi, sức khỏe; có bằng hoặc chứng chỉ phù hợp và giấy phép lái xe còn điểm, còn hiệu lực hoặc chứng chỉ bồi dưỡng kiến thức pháp luật giao thông; mang giấy tờ theo quy định.

*Căn cứ: Điều 56 khoản 2; Điều 59 khoản 1.*

#### GT25

**Câu hỏi:**
Người điều khiển xe thô sơ khi tham gia giao thông phải đáp ứng các điều kiện gì?

**Đáp án tham chiếu:**
Người điều khiển xe thô sơ phải tuân thủ quy tắc chung, đi đúng phần đường, giữ an toàn cho người khác và xếp hàng hóa theo giới hạn áp dụng cho loại xe. Điều kiện hoạt động chi tiết của xe thô sơ do văn bản hướng dẫn quy định.

*Căn cứ: Điều 30–32; Điều 35 khoản 5.*

### 6.2. QA Pilot – Lao động, tiền lương

#### LD01

**Câu hỏi:**
Hợp đồng lao động được giao kết qua phương tiện thông tin điện tử dưới hình thức thông điệp dữ liệu có giá trị như hợp đồng lao động bằng văn bản không?

**Đáp án tham chiếu:**
Có. Hợp đồng lao động được giao kết qua phương tiện điện tử dưới dạng thông điệp dữ liệu theo pháp luật về giao dịch điện tử có giá trị như hợp đồng lao động bằng văn bản.

*Căn cứ: Điều 14 khoản 1.*

#### LD02

**Câu hỏi:**
Chị A mở một siêu thị nhỏ ở nhà. Do bận con mọn, chị phải thuê một người làm thu ngân. Do đặc điểm thu ngân được quản lý tiền, sợ người làm không trung thực, nên chị A yêu cầu người đó phải đưa giấy tờ tùy thân cho chị giữ, chị mới cho ký kết hợp đồng lao động. Chị A có được quyền làm như vậy không?

**Đáp án tham chiếu:**
Không. Người sử dụng lao động không được giữ bản chính giấy tờ tùy thân, văn bằng, chứng chỉ của người lao động khi giao kết hoặc thực hiện hợp đồng.

*Căn cứ: Điều 17 khoản 1.*

#### LD03

**Câu hỏi:**
Theo quy định của pháp luật, những ai có thẩm quyền giao kết hợp đồng lao động?

**Đáp án tham chiếu:**
Phía người lao động do chính người lao động giao kết, trừ trường hợp được pháp luật cho phép ủy quyền. Phía người sử dụng lao động là người đại diện theo pháp luật hoặc người được ủy quyền và các chủ thể khác được nêu tại Điều 18; người được ủy quyền không được ủy quyền lại.

*Căn cứ: Điều 18.*

#### LD04

**Câu hỏi:**
Chị L là kế toán cho doanh nghiệp H. Để tăng thu nhập, chị nhận thêm việc quyết toán thuế cho một số cơ sở kinh doanh nhỏ lẻ vào cuối tháng và có ký kết hợp đồng lao động với các cơ sở kinh doanh này. Việc làm này của chị H có hợp pháp không?

**Đáp án tham chiếu:**
Có. Người lao động được ký nhiều hợp đồng lao động với nhiều người sử dụng lao động nhưng phải thực hiện đầy đủ các cam kết; nghĩa vụ bảo hiểm thực hiện theo pháp luật về bảo hiểm.

*Căn cứ: Điều 19.*

#### LD05

**Câu hỏi:**
D tốt nghiệp đại học và được nhận vào một công ty kinh doanh tài chính. Công ty quy định thời gian thử việc là 02 tháng, mức lương thử việc bằng 70% mức lương của công việc cho một người chính thức. A thấy như vậy là không hợp lý vì mình cũng làm như người khác mà chỉ nhận được 70% lương là không công bằng. A có thể đòi quyền lợi cho mình không?

**Đáp án tham chiếu:**
Thử việc tối đa 60 ngày có thể phù hợp với công việc cần trình độ từ cao đẳng trở lên. Tuy nhiên tiền lương thử việc phải ít nhất bằng 85% tiền lương của công việc đó, nên mức 70% là trái quy định.

*Căn cứ: Điều 25 khoản 1; Điều 26.*

#### LD06

**Câu hỏi:**
Những trường hợp nào người lao động được tạm hoãn hợp đồng lao động?

**Đáp án tham chiếu:**
Các trường hợp tạm hoãn gồm thực hiện nghĩa vụ quân sự; bị tạm giữ, tạm giam; chấp hành quyết định vào cơ sở bắt buộc; lao động nữ mang thai theo quy định; được bổ nhiệm làm người quản lý doanh nghiệp nhà nước và các trường hợp khác được hai bên thỏa thuận.

*Căn cứ: Điều 30.*

#### LD07

**Câu hỏi:**
Sau khi về hưu, do có chuyên môn về giám định trang sức, tôi có nhận lời làm việc cho một công ty vàng bạc đá quý, nhưng tôi muốn chỉ đi làm 3 ngày trong tuần, vì tôi muốn dành thời gian nghỉ ngơi, giúp đỡ con cháu. Tôi có được yêu cầu như vậy với công ty không? Quyền lợi của tôi có gì khác những người làm toàn thời gian không?

**Đáp án tham chiếu:**
Có thể thỏa thuận làm việc không trọn thời gian, chẳng hạn ba ngày mỗi tuần. Người lao động làm không trọn thời gian được bình đẳng về quyền, nghĩa vụ và cơ hội, tiền lương được thỏa thuận tương ứng.

*Căn cứ: Điều 32.*

#### LD08

**Câu hỏi:**
Chị T đang kế toán cho công ty X theo hợp đồng lao động không xác định thời hạn. Nay chị T lập gia đình và chuyển đến thành phố khác sinh sống. Chị T có thể chấm dứt hợp đồng lao động với công ty X được không?

**Đáp án tham chiếu:**
Người lao động theo hợp đồng không xác định thời hạn có quyền đơn phương chấm dứt hợp đồng, thông thường phải báo trước ít nhất 45 ngày; các trường hợp tại khoản 2 có thể nghỉ không cần báo trước.

*Căn cứ: Điều 35 khoản 1 điểm a và khoản 2.*

#### LD09

**Câu hỏi:**
Tôi mới về làm việc tại doanh nghiệp chuyên sản xuất bao bì sản phẩm với quy mô khoảng gần 200 người lao động. Hiện tại tôi đang tìm hiểu các quy định về đối thoại tại nơi làm việc. Xin hỏi theo quy định của pháp luật hiện hành, người sử dụng lao động phải tổ chức đối thoại tại nơi làm việc trong những trường hợp nào?

**Đáp án tham chiếu:**
Người sử dụng lao động phải tổ chức đối thoại định kỳ ít nhất một năm một lần; đối thoại khi một hoặc các bên yêu cầu và khi phát sinh các trường hợp pháp luật liệt kê như xây dựng thang, bảng lương hoặc xử lý sự kiện liên quan quyền lợi người lao động.

*Căn cứ: Điều 63 khoản 2.*

#### LD10

**Câu hỏi:**
X là công nhân nhà máy, vừa bị tai nạn lao động nên đang nghỉ theo chế độ. Sắp đến kỳ trả lương hàng tháng, trường hợp X không thể đến nhận lương thì phải giải quyết như thế nào để bảo đảm quyền lợi? Được biết công ty của X chỉ trả lương bằng tiền mặt.

**Đáp án tham chiếu:**
Khi người lao động không thể trực tiếp nhận lương, người sử dụng lao động có thể trả cho người được người lao động ủy quyền hợp pháp; cần lưu chứng cứ ủy quyền và thanh toán đúng kỳ hạn.

*Căn cứ: Điều 94 khoản 1.*

#### LD11

**Câu hỏi:**
Đề nghị cho biết phạm vi điều chỉnh, đối tượng áp dụng của Bộ luật Lao động 2019?

**Đáp án tham chiếu:**
Bộ luật Lao động 2019 quy định tiêu chuẩn lao động và quyền, nghĩa vụ, trách nhiệm của các bên trong quan hệ lao động cùng quản lý nhà nước về lao động. Đối tượng áp dụng gồm người lao động, người sử dụng lao động và chủ thể liên quan.

*Căn cứ: Điều 1–2.*

#### LD12

**Câu hỏi:**
Người lao động có những quyền và nghĩa vụ gì?

**Đáp án tham chiếu:**
Người lao động có quyền lựa chọn việc làm, hưởng lương, được bảo đảm an toàn, nghỉ ngơi, tham gia đại diện và đối thoại, từ chối việc có nguy cơ trực tiếp cho tính mạng, đơn phương chấm dứt hợp đồng, đình công; đồng thời phải thực hiện hợp đồng, nội quy và pháp luật liên quan.

*Căn cứ: Điều 5.*

#### LD13

**Câu hỏi:**
Đề nghị cho biết quyền và nghĩa vụ của người sử dụng lao động?

**Đáp án tham chiếu:**
Người sử dụng lao động có quyền tuyển dụng, quản lý, khen thưởng, xử lý kỷ luật và tham gia đối thoại, thương lượng; đồng thời phải thực hiện hợp đồng, tôn trọng nhân phẩm người lao động, đối thoại và chấp hành pháp luật lao động, bảo hiểm, an toàn vệ sinh lao động.

*Căn cứ: Điều 6.*

#### LD14

**Câu hỏi:**
Đề nghị cho biết các hành vi bị nghiêm cấm trong lĩnh vực lao động?

**Đáp án tham chiếu:**
Các hành vi bị cấm gồm phân biệt đối xử, ngược đãi hoặc cưỡng bức lao động, quấy rối tình dục tại nơi làm việc, lợi dụng đào tạo để trục lợi hoặc bóc lột, sử dụng lao động chưa thành niên trái luật và dụ dỗ, lừa gạt lao động theo quy định.

*Căn cứ: Điều 8.*

#### LD15

**Câu hỏi:**
Hợp đồng lao động là gì? Có mấy hình thức hợp đồng lao động?

**Đáp án tham chiếu:**
Hợp đồng lao động là thỏa thuận về việc làm có trả công, tiền lương, điều kiện lao động, quyền và nghĩa vụ của mỗi bên. Hợp đồng thường bằng văn bản hoặc thông điệp dữ liệu điện tử; lời nói chỉ áp dụng trong trường hợp luật cho phép.

*Căn cứ: Điều 13–14.*

#### LD16

**Câu hỏi:**
Đề nghị cho biết nguyên tắc giao kết hợp đồng lao động và nghĩa vụ cung cấp thông tin khi giao kết hợp đồng lao động?

**Đáp án tham chiếu:**
Giao kết hợp đồng phải tự nguyện, bình đẳng, thiện chí, hợp tác, trung thực và không trái pháp luật. Hai bên có nghĩa vụ cung cấp trung thực các thông tin cần thiết về công việc, điều kiện lao động và người lao động.

*Căn cứ: Điều 15–16.*

#### LD17

**Câu hỏi:**
Bộ luật Lao động 2019 quy định hợp đồng lao động có những loại nào?

**Đáp án tham chiếu:**
Có hai loại: hợp đồng không xác định thời hạn và hợp đồng xác định thời hạn không quá 36 tháng kể từ ngày có hiệu lực.

*Căn cứ: Điều 20 khoản 1.*

#### LD18

**Câu hỏi:**
Việc sửa đổi, bổ sung hợp đồng lao động được quy định như thế nào?

**Đáp án tham chiếu:**
Bên muốn sửa đổi, bổ sung hợp đồng phải báo cho bên kia trước ít nhất ba ngày làm việc. Nếu thống nhất thì ký phụ lục hoặc hợp đồng mới; nếu không thống nhất thì tiếp tục hợp đồng đã giao kết.

*Căn cứ: Điều 33.*

#### LD19

**Câu hỏi:**
Đề nghị cho biết các trường hợp chấm dứt hợp đồng lao động?

**Đáp án tham chiếu:**
Hợp đồng chấm dứt khi hết hạn hoặc hoàn thành công việc; hai bên thỏa thuận; người lao động hoặc người sử dụng lao động đơn phương đúng luật; người lao động chết hoặc mất năng lực theo luật; bị sa thải; doanh nghiệp chấm dứt hoạt động và các trường hợp khác theo quy định.

*Căn cứ: Điều 34.*

#### LD20

**Câu hỏi:**
Người lao động được đơn phương chấm dứt hợp đồng lao động mà không phải báo trước cho người sử dụng lao động trong trường hợp nào?

**Đáp án tham chiếu:**
Người lao động có thể nghỉ không báo trước khi không được bố trí đúng công việc, không được trả đủ hoặc đúng hạn lương; bị ngược đãi, quấy rối tình dục; lao động nữ mang thai phải nghỉ theo chỉ định; đủ tuổi nghỉ hưu; hoặc người sử dụng lao động cung cấp thông tin không trung thực ảnh hưởng việc thực hiện hợp đồng.

*Căn cứ: Điều 35 khoản 2.*

#### LD21

**Câu hỏi:**
Pháp luật lao động quy định về tiền lương và việc trả lương như thế nào?

**Đáp án tham chiếu:**
Tiền lương là số tiền người sử dụng lao động trả theo thỏa thuận để thực hiện công việc, gồm mức lương, phụ cấp và khoản bổ sung; phải trả trực tiếp, đầy đủ, đúng hạn, trừ trường hợp trả qua người được ủy quyền hợp pháp.

*Căn cứ: Điều 90; Điều 94–97.*

#### LD22

**Câu hỏi:**
Thời giờ làm việc của người chưa thành niên được pháp luật quy định như thế nào?

**Đáp án tham chiếu:**
Người từ đủ 15 đến dưới 18 tuổi làm việc tối đa 8 giờ/ngày, 40 giờ/tuần; người dưới 15 tuổi tối đa 4 giờ/ngày, 20 giờ/tuần và không làm thêm giờ, làm đêm. Việc sử dụng lao động chưa thành niên còn chịu các giới hạn công việc tại các điều liên quan.

*Căn cứ: Điều 146.*

#### LD23

**Câu hỏi:**
Thời gian gần đây, do khối lượng công việc quá lớn nên Dũng được người sử dụng lao động yêu cầu làm thêm giờ và làm thêm cả vào ngày nghỉ (thứ 7, chủ nhật). Tuy nhiên, đến lúc trả lương, Dũng chỉ nhận được mức tiền lương như bình thường. Khi Dũng thắc mắc thì người sử dụng lao động trả lời rằng: Việc làm thêm giờ là yêu cầu bắt buộc của công việc nên không phải trả lương. Xin hỏi, điều đó đúng hay sai? Pháp luật quy định như thế nào trong trường hợp này?

**Đáp án tham chiếu:**
Trả lương làm thêm giờ ít nhất 150% vào ngày thường, 200% vào ngày nghỉ hằng tuần và 300% vào ngày lễ, Tết, ngày nghỉ có hưởng lương, chưa kể tiền lương ngày lễ đối với người hưởng lương ngày. Không thể trả như giờ làm bình thường.

*Căn cứ: Điều 98 khoản 1.*

#### LD24

**Câu hỏi:**
Khi làm thêm giờ vào ngày nghỉ lễ, tết mà trùng với ngày nghỉ hằng tuần thì người lao động được tính trả lương như thế nào?

**Đáp án tham chiếu:**
Nếu làm thêm vào ngày lễ, Tết, mức ít nhất là 300% chưa kể lương ngày lễ đối với người hưởng lương ngày. Khi ngày lễ trùng ngày nghỉ hằng tuần, người lao động được nghỉ bù vào ngày làm việc kế tiếp theo quy định.

*Căn cứ: Điều 98 khoản 1 điểm c; Điều 112 khoản 3.*

#### LD25

**Câu hỏi:**
Người sử dụng lao động có trách nhiệm thanh toán tiền “phép năm” còn dư trong những trường hợp nào?

**Đáp án tham chiếu:**
Khi thôi việc hoặc mất việc làm mà chưa nghỉ hoặc chưa nghỉ hết phép năm, người sử dụng lao động phải trả tiền lương cho những ngày chưa nghỉ.

*Căn cứ: Điều 113 khoản 3.*

### 6.3. Trạng thái của bộ QA sau W1

Đến cuối W1, nhóm đã có đủ 50/50 câu QA pilot, gồm 25 câu Giao thông vận tải và 25 câu Lao động – tiền lương.

Các câu hỏi đã được gắn đáp án tham chiếu và căn cứ điều khoản trong corpus. Tuy nhiên, bộ QA hiện vẫn được xem là pilot dataset, chưa phải gold benchmark cuối cùng.

Trong các tuần tiếp theo, nhóm sẽ tiếp tục:

- đối chiếu đáp án với nguồn văn bản pháp luật chính thức;
- kiểm tra trạng thái hiệu lực tại snapshot date 01/07/2026;
- kiểm tra các văn bản sửa đổi, bổ sung hoặc thay thế;
- chuẩn hóa citation;
- hoàn thiện metadata phục vụ truy vết;
- rà soát các câu hỏi có thể có nhiều cách diễn giải;
- khóa phiên bản QA dùng làm benchmark sau khi hoàn tất kiểm chứng.

## 7. Giao thức đánh giá — Evaluation Protocol

Đơn vị đánh giá là một câu hỏi, một đáp án chuẩn và ít nhất một điều khoản nguồn. Bộ pilot gồm 25 câu giao thông và 25 câu lao động, giữ nguyên câu hỏi của CSV; đáp án được đối chiếu với văn bản thuộc corpus. Các câu hỏi dùng để thiết kế và kiểm tra ban đầu; khi đánh giá chính thức phải tách tập kiểm thử độc lập, không dùng để chỉnh prompt, ngưỡng hoặc chọn checkpoint.

Điều kiện chạy: chỉ nạp 53 văn bản và chỉ hai lĩnh vực đã chốt; ghi phiên bản corpus, cấu hình mô hình, prompt, tham số truy xuất, thời gian chạy và seed nếu có. Tắt tìm kiếm web khi đo grounding theo corpus; chạy mỗi câu trong phiên độc lập để tránh lịch sử hội thoại. Câu ngoài phạm vi hoặc thiếu căn cứ phải được hệ thống từ chối hoặc nêu rõ không đủ nguồn.

Truy xuất: dùng biến thể truy vấn từ Planner, PyVi và Qdrant lấy top 25 mỗi truy vấn, hợp nhất RRF top 50 rồi CrossEncoder xếp lại top 5. Báo cáo Hit@1/3/5, MRR@5, nDCG@5 và Precision@5 với nhãn điều khoản; lưu top 5 kèm điểm và nguồn. Các câu không có nhãn điều khoản chuẩn chưa được tính là đúng truy xuất.

Toàn hệ thống: Orchestrator dùng trích xuất BERT, Grader với ngưỡng 0,6 và tối đa hai vòng lặp truy xuất, Generate và Hallucination Checker. So sánh đáp án tạo với đáp án chuẩn bằng token F1, ROUGE-L và cosine ngữ nghĩa như mã đánh giá hiện có. Chấm thủ công bổ sung theo ba tiêu chí: đúng pháp lý tại mốc 01/07/2026, dẫn đúng điều khoản, không khẳng định vượt nguồn; mỗi tiêu chí 0/1/2, hai người rà soát bất đồng và ghi lý do. Báo cáo trung bình từng lĩnh vực, toàn bộ, tỷ lệ từ chối đúng và các trường hợp sai nghiêm trọng. Không dùng các điểm số lịch sử của corpus khác làm kết quả W1.

## 8. Ethics và giới hạn sử dụng

Hệ thống được xây dựng nhằm phục vụ mục đích:

- Hỗ trợ tra cứu văn bản pháp luật.
- Hỗ trợ học tập và nghiên cứu.
- Hỗ trợ người dùng xác định các văn bản và điều khoản có khả năng liên quan đến câu hỏi.

Hệ thống không được xem là công cụ thay thế tư vấn pháp lý chuyên nghiệp.

Pháp luật có thể được sửa đổi, bổ sung, đình chỉ, thay thế hoặc chịu các quy định chuyển tiếp. Vì vậy, câu trả lời cần gắn với căn cứ pháp lý và mốc thời gian phù hợp.

Trong trường hợp:

- corpus không chứa đủ văn bản cần thiết;
- các nguồn có dấu hiệu mâu thuẫn;
- không tìm thấy căn cứ phù hợp;
- câu hỏi phụ thuộc nhiều vào tình tiết cụ thể của một vụ việc;

hệ thống cần nêu rõ giới hạn thay vì tự suy đoán hoặc tạo ra căn cứ không tồn tại.

Dữ liệu cá nhân của người sử dụng không được đưa vào corpus hoặc dataset đánh giá nếu không cần thiết. Các tình huống QA cần hạn chế hoặc loại bỏ thông tin có khả năng xác định danh tính cá nhân.

Khi công bố dữ liệu hoặc repository, nhóm cần xem xét quyền sử dụng và quyền tái phân phối các tài liệu được sử dụng.

## 9. Kết quả thực hiện W1

Đến cuối W1, nhóm đã hoàn thành các nội dung sau:

| Công việc | Trạng thái |
| --- | --- |
| Chốt hai lĩnh vực pháp luật | Hoàn thành |
| Xác định nguồn dữ liệu pháp luật | Hoàn thành |
| Chốt snapshot date 01/07/2026 | Hoàn thành |
| Xác định corpus 53 văn bản | Hoàn thành |
| Corpus Plan | Hoàn thành |
| Bộ 50 QA pilot | Hoàn thành |
| Evaluation Protocol | Hoàn thành |
| Ethics / Scope Note | Hoàn thành |
| GitHub repository | Đã thiết lập / cập nhật |
| Chạy benchmark retrieval | Chưa thực hiện trong W1 |
| Chạy đánh giá toàn hệ thống | Chưa thực hiện trong W1 |
| Metadata/manifest hoàn chỉnh | Chuyển sang giai đoạn tiếp theo |

Tuần W1 chưa có kết quả chạy mô hình nên chưa báo cáo các chỉ số retrieval hoặc chất lượng câu trả lời thực nghiệm.

## 10. Công việc chuyển sang tuần tiếp theo

Các công việc liên quan tới metadata và quản lý corpus chi tiết được chuyển sang tuần sau, bao gồm:

- Xây dựng manifest cho toàn bộ corpus.
- Bổ sung mã hiệu văn bản.
- Chuẩn hóa tên văn bản.
- Bổ sung cơ quan ban hành.
- Bổ sung ngày ban hành.
- Liên kết từng văn bản với nguồn công bố chính thức.
- Ghi nhận ngày truy cập nguồn.
- Tính hash tệp phục vụ kiểm tra tính toàn vẹn.
- Xác minh và ghi nhận trạng thái hiệu lực.
- Xác định quan hệ sửa đổi, bổ sung, thay thế giữa các văn bản.
- Kiểm tra và chuẩn hóa các trường metadata.
- Tiếp tục kiểm chứng đáp án của bộ QA trước khi khóa gold benchmark.

Các bước triển khai và đánh giá thực nghiệm của hệ thống sẽ được thực hiện theo kế hoạch của các tuần tiếp theo.

## 11. Kết luận W1

Trong tuần W1, nhóm đã hoàn thành các công việc nền tảng cần thiết để xác định phạm vi và thiết kế quy trình đánh giá cho hệ thống hỏi đáp pháp luật.

Phạm vi của hệ thống được giới hạn ở hai lĩnh vực Giao thông vận tải và Lao động – tiền lương, với corpus ban đầu gồm 53 văn bản và bộ 50 QA pilot.

Nguồn dữ liệu được định hướng dựa trên các nguồn công bố pháp luật chính thức. Snapshot date được chốt tại ngày 01/07/2026 nhằm tạo một mốc thống nhất cho việc xây dựng đáp án và đánh giá hệ thống.

Evaluation Protocol đã được xác định nhưng chưa được sử dụng để báo cáo điểm thực nghiệm trong W1.

Các công việc chi tiết liên quan tới metadata, manifest, xác minh tình trạng hiệu lực và quan hệ sửa đổi của từng văn bản sẽ được triển khai ở tuần tiếp theo.

## Phụ lục A. Bộ 50 QA Pilot

Phụ lục gồm:

- A1. Giao thông vận tải: 25 câu.
- A2. Lao động – tiền lương: 25 câu.

Mỗi câu bao gồm:

1. Câu hỏi gốc.
2. Đáp án tham chiếu.
3. Điều khoản/văn bản được sử dụng làm căn cứ.

Các đáp án trong bộ pilot hiện được xem là đáp án tham chiếu ban đầu. Những nội dung liên quan đến mức tiền, điều kiện áp dụng, trạng thái hiệu lực hoặc quan hệ sửa đổi cần tiếp tục được kiểm chứng trước khi sử dụng làm gold benchmark chính thức.

## Nguồn tham khảo

1. Cơ sở dữ liệu quốc gia về văn bản pháp luật.
2. Công báo điện tử.
3. Cổng thông tin điện tử của các cơ quan có thẩm quyền ban hành văn bản.
4. Bộ luật Lao động số 45/2019/QH14.
5. Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15.
6. Nghị định số 168/2024/NĐ-CP và các văn bản có liên quan trong phạm vi corpus.
