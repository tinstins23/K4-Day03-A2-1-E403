# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)
*Dành cho Role 5: Observability & Reviewer*

**Đề tài**: RentMate — Trợ Lý Tìm & Đặt Lịch Xem Nhà Trọ / Căn Hộ Cho Thuê
**Nhóm**: A2-1 — E403 · **Cập nhật**: 2026-07-28

---

## 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

> **Câu hỏi cần trả lời**: Bài toán này có thực sự CẦN Agent, hay Chatbot thuần là đủ?

| Tiêu chí | Điểm (1-5) | Lý do đánh giá (dẫn chứng từ `data/`) |
| :--- | :---: | :--- |
| 🧠 **Multi-step Reasoning** | `5/5` | Một yêu cầu thật của người thuê nhà kéo theo chuỗi 4–5 bước phụ thuộc nhau: lọc căn theo ngân sách/khu vực ➔ đọc chi tiết căn ➔ tra thông tin chủ nhà ➔ xem lịch trống ➔ đặt lịch. Không thể rút gọn thành 1 bước vì **input của bước sau là output của bước trước** (phải có `property_id` mới tra được slot, phải có `slot_id` mới đặt được lịch). |
| 🛠️ **Tool Interaction** | `5/5` | 100% dữ liệu nghiệp vụ nằm **ngoài** LLM: 15 căn hộ, 7 chủ nhà, 31 khung giờ trong `data/*.json`. LLM không thể biết P006 giá 4.8 triệu hay SĐT chủ nhà LL03 là gì. Không gọi tool = chắc chắn bịa. Đây cũng là tool có **side-effect thật** (`book_viewing` ghi vào `bookings.json`), không chỉ tra cứu read-only. |
| 🔀 **Dynamic Decision** | `5/5` | Đường đi rẽ nhánh theo dữ liệu quan sát được, không đoán trước từ câu hỏi: `status = rented` (P009, P012) ➔ loại khỏi kết quả; `status = pending` (P015) ➔ tìm thấy nhưng **từ chối đặt lịch**; P013 còn trống nhưng **kín 100% slot** ➔ phải quay lại đề xuất căn khác. Cùng một câu hỏi, dữ liệu khác ➔ hành động khác. |
| ⏳ **Long Horizon** | `3/5` | **Điểm yếu của đề tài.** Toàn bộ quy trình gói gọn trong 1 phiên hội thoại 4–5 bước, kết thúc rõ ràng khi đặt được lịch. Chưa cần bộ nhớ dài hạn hay theo dõi qua nhiều ngày (kiểu nhắc lịch trước 1 tiếng, thương lượng giá qua nhiều lượt). Đây là tác vụ **trung hạn**, không phải long-horizon thực sự. |
| **TỔNG ĐIỂM FIT** | **18/20** | **KẾT LUẬN: BÀI TOÁN RẤT PHÙ HỢP DÙNG REACT AGENT.** |

### Thang quy đổi

| Tổng điểm | Kết luận |
| :---: | :--- |
| 4–8 | Chatbot thuần là đủ, dùng Agent chỉ tốn chi phí |
| 9–13 | Cân nhắc — có thể dùng 1 lần gọi tool đơn giản (function calling), chưa cần ReAct loop |
| 14–20 | **Nên dùng ReAct Agent** ✅ ← nhóm mình ở đây |

---

## ⚖️ 2. PHẢN BIỆN — KHI NÀO CHATBOT VẪN THẮNG?

> Chuẩn bị trước cho Mốc 4 (Cross-Audit). Nhóm khác chắc chắn sẽ tấn công vào chỗ này.

CODELAB cảnh báo: *"Đừng vội kết luận Agent luôn thắng"*. Nhóm mình tự nhận:

| Loại câu hỏi | Nên đi đường nào | Vì sao |
| :--- | :--- | :--- |
| *"Đặt cọc thuê nhà thường là mấy tháng?"* | 🤖 **Chatbot** | Kiến thức chung, không cần tra dữ liệu. Agent gọi tool ở đây là **lãng phí**: chậm hơn, tốn token hơn, mà kết quả không tốt hơn. |
| *"Hợp đồng thuê nhà cần giấy tờ gì?"* | 🤖 **Chatbot** | Tương tự — tư vấn quy trình, không có gì để tra. |
| *"Tìm phòng dưới 4 triệu ở Cầu Giấy"* | 🧠 **Agent** | Bắt buộc đọc `properties.json`. |
| *"Đặt lịch xem P006 sáng mai"* | 🧠 **Agent** | Có hành động ghi dữ liệu. |

**Chi phí orchestration của Agent chỉ đáng giá khi câu hỏi cần bằng chứng từ dữ liệu, hoặc cần thực hiện một hành động.** Với 2 câu đầu bảng trên, Agent **thua** Chatbot về cả tốc độ lẫn chi phí. Đây là lý do nhóm sẽ vẽ **Hybrid Flowchart** ở Mốc 4 để phân luồng, thay vì đẩy mọi câu hỏi qua Agent.

### Điểm yếu tự nhận của đề tài

1. **Long Horizon chỉ 3/5** — nếu bị chất vấn, nhóm thừa nhận và chỉ ra hướng nâng cấp: thêm Memory để agent nhớ ngân sách/khu vực ưa thích của khách qua nhiều phiên (chính là phần Bonus Cấp 4).
2. **Dữ liệu tĩnh** — mock data không đổi theo thời gian thực như giá vé máy bay. Bù lại, `book_viewing` **ghi thật** vào `bookings.json`, nên trạng thái hệ thống vẫn thay đổi được trong lúc demo.

---

## 🔍 3. SO SÁNH PHẢN HỒI CHATBOT vs AGENT

> ⏳ **CHƯA CHẠY** — điền sau khi Role 4 hoàn thành `src/app.py` ở Mốc 2 & Mốc 3.
> Chỉ dán **log thật** copy từ terminal. Tuyệt đối không tự viết tay trace giả — coach sẽ đối chiếu với code.

### Test Case #___ : *"..."*

**🤖 Chatbot Baseline**
* Số lần gọi tool: `___` (phải = 0)
* Phản hồi: *(dán nguyên văn)*
* Phân loại: ☐ correct ☐ safe fallback ☐ **hallucinated**
* Nhận xét:

**🧠 ReAct Agent**
```text
(dán nguyên chuỗi Thought / Action / Observation / Final Answer từ terminal)
```
* Số vòng lặp đã dùng: `___ / MAX_ITERATIONS`
* Nhận xét:

---

## 📋 4. BẢNG ĐÁNH GIÁ 5 TEST CASES (RUBRIC 0–2 ĐIỂM)

> ⏳ **CHƯA CHẠY** — điền ở Mốc 3.

| # | Loại | Hệ thống | Factual correctness | Grounding | Tool selection | Termination | Tổng /8 |
| :-: | :--- | :--- | :-: | :-: | :-: | :-: | :-: |
| 1 | 🟢 Đơn giản | Chatbot | | | | | |
| 1 | 🟢 Đơn giản | Agent | | | | | |
| 2 | 🟢 Đơn giản | Chatbot | | | | | |
| 2 | 🟢 Đơn giản | Agent | | | | | |
| 3 | 🟡 1 Tool | Chatbot | | | | | |
| 3 | 🟡 1 Tool | Agent | | | | | |
| 4 | 🟡 2 Tools | Chatbot | | | | | |
| 4 | 🟡 2 Tools | Agent | | | | | |
| 5 | 🔴 Edge case | Chatbot | | | | | |
| 5 | 🔴 Edge case | Agent | | | | | |

**Thang điểm mỗi ô**: 0 = sai/bịa · 1 = đúng một phần · 2 = đúng hoàn toàn

---

## 🐛 5. FAILED TRACE & PHÂN TÍCH NGUYÊN NHÂN GỐC (RCA)

> ⏳ **CHƯA CHẠY** — điền ở Mốc 4, cần ít nhất 1 failed trace thật.

| Mục | Nội dung |
| :--- | :--- |
| **Triệu chứng** | |
| **Trace lỗi (Before)** | |
| **Nguyên nhân gốc** | |
| **Cách sửa ở Agent V2** | |
| **Trace sau khi sửa (After)** | |
