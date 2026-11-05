"""Scope-only prompt material; no routing, retry or error-policy replacement."""
import json
from pathlib import Path

SCOPE_PATH = Path(__file__).resolve().parents[1] / 'core/corpus_scope.json'

def load_scope():
    scope = json.loads(SCOPE_PATH.read_text(encoding='utf-8'))
    assert len(scope['documents']) == 53
    assert set(scope['domains']) == {'giaoThong_VanTai', 'laoDong_TienLuong'}
    expected={f'giaoThong_VanTai-{i}' for i in range(1,40) if i!=8}
    expected|={f'laoDong_TienLuong-{i}' for i in range(1,22) if i not in {3,6,10,12,14,20}}
    if {d['id'] for d in scope['documents']}!=expected:
        raise ValueError('Scope must use exactly the approved 53 document IDs')
    return scope

def narrow_planner_prompt(original):
    scope = load_scope()
    original = original.replace(
        '- `legal`: câu hỏi pháp luật Việt Nam, có thể trả lời từ CSDL văn bản luật.',
        '- `legal`: câu hỏi thuộc Giao thông vận tải hoặc Lao động tiền lương, có thể tra cứu trong corpus 53 văn bản đã chốt.'
    ).replace(
        '- `out_of_scope`: câu hỏi ngoài luật VN và không thuộc realtime (kiến thức khác,',
        '- `out_of_scope`: câu hỏi ngoài hai lĩnh vực/corpus đã chốt và không thuộc realtime (bao gồm lĩnh vực luật khác, kiến thức khác,'
    )
    substitutions = {
        'điều kiện kết hôn theo pháp luật Việt Nam là gì':'tiền lương thử việc theo pháp luật lao động được quy định thế nào',
        'Điều kiện kết hôn theo pháp luật Việt Nam hiện hành':'Quy định về tiền lương thử việc trong Bộ luật Lao động 2019',
        'Câu hỏi pháp luật hôn nhân gia đình, tra CSDL văn bản luật.':'Câu hỏi pháp luật lao động tiền lương, tra corpus đã chốt.',
        'Thông tư 57/2015/TT-BYT quy định điều kiện sức khỏe người làm IVF như thế nào':'Thông tư 36/2024/TT-BYT quy định tiêu chuẩn sức khỏe người lái xe như thế nào',
        'Thông tư 57/2015/TT-BYT của Bộ Y tế quy định điều kiện sức khỏe người thực hiện kỹ thuật thụ tinh trong ống nghiệm':'Thông tư 36/2024/TT-BYT của Bộ Y tế quy định tiêu chuẩn sức khỏe của người lái xe',
        '"NoibanHanhFilter":"Bộ Y tế","NgayBanHanhFilter":"2015"':'"NoibanHanhFilter":"Bộ Y tế","NgayBanHanhFilter":"2024"',
    }
    for before, after in substitutions.items():
        original=original.replace(before,after)
    listing = '\n'.join(f"- {d['id']} | {d['number']} | {d['title']}" for d in scope['documents'])
    return original + '\n\n## PHẠM VI CORPUS BẮT BUỘC\n' + (
        'Chỉ Giao thông vận tải và Lao động tiền lương. Luật hôn nhân/gia đình, giáo dục, đất đai, hình sự độc lập và các lĩnh vực khác không thuộc legal/RAG của bản này. '
        'Câu hỏi chung trong hai lĩnh vực được tra cứu từ danh sách dưới đây; nếu người hỏi yêu cầu một văn bản cụ thể nằm ngoài danh sách, không coi đó là văn bản có trong corpus. '
        'Giữ nguyên schema intent/tool và bảng routing theo web_search_enabled ở trên. Không tự bật web. '
        'Mốc tham chiếu 01/07/2026; hiệu lực từng văn bản chưa được xác minh đầy đủ, không suy ra hiệu lực từ ngày ban hành.\n' + listing
    )
