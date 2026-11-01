# Nguồn code và checkpoint

Các module embedding, CrossEncoder và RRF sử dụng từ [bhuy71/Vietnamese-Legal-QA-System-using-Agentic-RAG-and-Fine-Tuned-Language-Models](https://github.com/bhuy71/Vietnamese-Legal-QA-System-using-Agentic-RAG-and-Fine-Tuned-Language-Models), source HEAD tham chiếu `8c151b082635d17f74619dcea5e17b6bb0b0b4be`. Hash code thực tế của lượt đo được lưu riêng; không đồng nhất source HEAD này với commit của repo nộp bài.

Checkpoint `bhuy71/embedding_finetuned` và `bhuy71/rerank_model` được dùng theo revisions trong `source_snapshot/models.json`; không tuyên bố đã tự huấn luyện chúng trong W4/W5. Reranker tham chiếu Alibaba-NLP/gte-multilingual-reranker-base. Không bổ sung một license mới bao trùm các thành phần tái sử dụng.
