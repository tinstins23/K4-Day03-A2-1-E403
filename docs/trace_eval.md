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

## 🔍 3. QUAN SÁT CHATBOT BASELINE (MỐC 2)

> ⚠️ **NGUYÊN TẮC**: chỉ dán **log thật** copy từ terminal. Tuyệt đối không tự viết tay trace giả — coach sẽ đối chiếu với code.
> Cột "Agent" để trống ở Mốc 2, sẽ điền ở Mốc 3 sau khi Role 4 lắp xong ReAct loop.

**Bộ test**: 5 câu trong `config/test_cases.json` (Role 1) · **Provider**: `gemini` (`GeminiProvider`) · **Model**: `gemini-flash-latest` · **Ngày chạy**: `2026-07-28`

> ⚙️ **Cách lấy log**: `src/app.py` của Role 4 hiện chỉ chạy đúng 1 câu (`tests[2]`, dòng 105) nên không lấy đủ 5 case. Tôi chạy một script phụ **import lại đúng `CHATBOT_BASELINE_PROMPT` (Role 3) + `get_llm_provider()` (providers.py)** rồi lặp qua cả 5 case — không sửa `src/app.py`. Log dưới đây là **nguyên văn stdout**.
>
> 📌 **Ghi chú model**: `.env` ban đầu để `gemini-2.5-flash`, Google đã ngừng cấp model này cho tài khoản mới (`404 NOT_FOUND ... no longer available to new users`). Đã đổi sang alias `gemini-flash-latest`. `.env` nằm trong `.gitignore` nên thay đổi này không đẩy lên Git — **các bạn khác gặp lỗi 404 thì tự sửa `LLM_MODEL` trong `.env` máy mình.**

### Điều cần soi ở Mốc 2

| Dấu hiệu cần bắt | Vì sao quan trọng |
| :--- | :--- |
| 🔴 **Ảo giác (hallucination)** | Chatbot tự bịa tên nhà trọ, giá thuê, số điện thoại chủ nhà — nghe rất thật nhưng không có trong `data/properties.json`. Đây là thứ cần chụp lại làm bằng chứng. |
| 🟡 **Safe fallback** | Chatbot thành thật nói "tôi không có dữ liệu thời gian thực" — không sai, nhưng **cũng không giúp được gì** cho người dùng. |
| 🔴 **Nhận vơ hành động** | Chatbot nói "đã đặt lịch xong cho bạn" trong khi `bookings.json` không hề đổi. Nguy hiểm nhất vì người dùng tin là thật. |
| ✅ **Tool calls = 0** | Phải xác nhận bằng code path, không tin vào giọng văn mượt mà của câu trả lời. |

---

### Test Case #1 — 🟢 Đơn giản
> *"Khi thuê trọ ở Hà Nội thường phải đặt cọc mấy tháng và hợp đồng thuê nhà cần giấy tờ gì?"*

**🤖 Chatbot Baseline** · Số lần gọi tool: `0` ✅
```text
*Lưu ý: Tôi là hệ thống tư vấn tự động, không trực tiếp quản lý hay có dữ liệu thực tế về bất kỳ căn trọ cụ thể nào. Dưới đây là thông tin tổng quan dựa trên thực tế thị trường cho thuê tại Hà Nội:*

### 1. Thông thường thuê trọ ở Hà Nội đặt cọc mấy tháng?

* **Phòng trọ / Căn hộ dịch vụ nhỏ:** Phổ biến nhất là đặt cọc **1 tháng** tiền nhà.
* **Chung cư / Căn hộ nguyên căn / Nhà nguyên căn:** Thường đặt cọc từ **1 đến 2 tháng** tiền nhà (tùy thuộc vào giá trị nội thất và thỏa thuận với chủ nhà).
* **Hình thức thanh toán phổ biến:**
  * *"Đóng 1 cọc 1"* (Trả tiền nhà từng tháng + cọc 1 tháng).
  * *"Đóng 3 cọc 1"* (Trả tiền nhà 3 tháng/lần + cọc 1 tháng).

### 2. Hợp đồng thuê nhà cần những giấy tờ gì?

**Đối với người thuê nhà (bạn cần chuẩn bị):**
* **Căn cước công dân (CCCD)** hoặc Hộ chiếu (bản gốc để đối chiếu và bản photo/hình ảnh để đính kèm hợp đồng).
* Thông tin cá nhân để chủ nhà làm thủ tục **đăng ký tạm trú** với Công an khu vực.

**Đối với chủ nhà (bạn nên yêu cầu chủ nhà cung cấp/cho xem):**
* **CCCD** của chủ nhà (để đối chiếu thông tin trên hợp đồng).
* **Giấy chứng nhận quyền sở hữu nhà đất (Sổ đỏ/Sổ hồng)** hoặc hợp đồng mua bán nhà để xác minh chính chủ.
* *Lưu ý:* Nếu thuê lại từ người khác (thuê lại/môi giới), hãy yêu cầu xem **Giấy ủy quyền cho thuê** hoặc **Hợp đồng thuê gốc** cho phép cho thuê lại.

### 💡 Lời khuyên trước khi ký hợp đồng:
1. **Điều khoản hoàn cọc:** Đọc kỹ quy định về thời hạn báo trước khi chuyển đi (thường là 1 tháng) để được nhận lại tiền cọc đầy đủ.
2. **Chi phí phát sinh:** Xác nhận rõ giá điện, nước, internet, phí dịch vụ, vệ sinh, giữ xe trên hợp đồng.
3. **Biên bản bàn giao:** Kiểm tra và ghi lại tình trạng trang thiết bị, số điện, số nước ban đầu trước khi đặt cọc/nhận phòng.
```
* Phân loại: ☑ **correct** ☐ safe fallback ☐ hallucinated
* Nhận xét: **Dự đoán đúng — đây là câu Chatbot thắng.** Trả lời khớp `ground_truth` (cọc 1–2 tháng, cần CCCD + hợp đồng + tạm trú), lại còn bổ sung thêm giá trị mà `data/` không có: cách "đóng 3 cọc 1", nhắc kiểm tra sổ đỏ chính chủ, biên bản bàn giao số điện/số nước.
* ➔ **Bằng chứng cho Hybrid Flowchart (Mốc 4)**: câu này mà đẩy qua Agent thì chỉ tốn thêm thời gian và token, kết quả không tốt hơn. Phải đi nhánh Chatbot.

---

### Test Case #2 — 🟡 Cần 1 Tool
> *"Tìm giúp tôi phòng trọ dưới 4 triệu ở quận Cầu Giấy."*

**🤖 Chatbot Baseline** · Số lần gọi tool: `0` ✅
```text
**Giới hạn hệ thống:**
Tôi không có quyền truy cập vào dữ liệu thời gian thực, hệ thống tin đăng hoặc cơ sở dữ liệu phòng trọ. Vì vậy, tôi **không thể cung cấp trực tiếp địa chỉ, số điện thoại chủ nhà hoặc danh sách phòng trọ cụ thể** đang trống tại quận Cầu Giấy.

Tuy nhiên, với ngân sách **dưới 4 triệu đồng/tháng** tại quận Cầu Giấy, tôi có thể tư vấn cho bạn kinh nghiệm và định hướng tìm kiếm như sau:

### 1. Khu vực gợi ý nên tập trung tìm kiếm
Ở Cầu Giấy, mức giá 2,5 - 4 triệu đồng thường rơi vào dòng phòng trọ khép kín, studio nhỏ hoặc chung cư mini trong ngõ:
* **Khu vực Mai Dịch, Doãn Kế Thiện, Trần Vĩ:** Nhiều phòng trọ sinh viên/người đi làm, giá tương đối dễ thở (2,5 - 3,5 triệu).
* **Khu vực Quan Hoa, Nguyễn Khánh Toàn, Đường Đường Bưởi:** Ngõ nhỏ sâu thường có phòng khép kín khoảng 3 - 4 triệu.
* **Khu vực Yên Hòa, Trung Kính (các ngõ sâu):** Nhiều chung cư mini giá từ 3,5 - 4 triệu.

### 2. Kênh tìm kiếm hiệu quả
* **Hội nhóm Facebook:** Tìm các nhóm như *"Tìm phòng trọ Cầu Giấy"*, *"Phòng trọ Sinh viên ĐH Quốc Gia/Sư Phạm/Thương Mại"*.
* **Trang web/Ứng dụng:** Chợ Tốt, Phongtro123, Batdongsan.com.vn (lọc theo Quận Cầu Giấy và khoảng giá dưới 4 triệu).
* **Đi khảo sát trực tiếp:** Đến các khu ngõ quanh các trường đại học lớn để xem biển treo "Còn phòng cho thuê".

### 3. Các chi phí cần làm rõ với chủ nhà
Ngoài tiền nhà (dưới 4 triệu), bạn cần hỏi kỹ để tránh vượt ngân sách:
* **Giá điện, nước:** Điện (thường 3.500 - 4.000đ/kWh), Nước (100.000đ/người hoặc theo khối).
* **Phí dịch vụ phát sinh:** Thang máy, vệ sinh, máy giặt chung, mạng internet, tiền gửi xe (tổng phụ phí thường từ 300.000 - 600.000đ/tháng).

### 4. Lưu ý quan trọng khi đi xem phòng
* **An toàn & PCCC:** Kiểm tra kỹ lối thoát hiểm, bình chữa cháy, hệ thống thang bộ và cửa vân tay/khóa cổng.
* **Đặt cọc & Hợp đồng:** Chỉ chuyển tiền cọc khi có giấy biên nhận rõ ràng. Đọc kỹ điều khoản về thời hạn báo chuyển đi (thường trước 30 ngày) và điều kiện hoàn cọc.

*(Nếu bạn có sẵn một danh sách các phòng đang cân nhắc, bạn có thể gửi thông tin/mô tả vào đây, tôi sẽ giúp bạn phân tích và so sánh ưu/nhược điểm từng phòng).*
```
* Phân loại: ☐ correct ☑ **safe fallback** ☐ hallucinated
* **Đối chiếu ground truth**: đáp án đúng duy nhất là **P001 – 3.200.000 VNĐ**. Chatbot có bịa ra căn nào khác không? ➔ **KHÔNG.** Nó không bịa ra tin đăng cụ thể nào. Tên/giá nó bịa: `(không có)`
* ⚠️ **Nhưng vẫn trượt**: nó **không hề nhắc tới P001** — căn duy nhất đúng yêu cầu. Người dùng hỏi "tìm giúp tôi phòng" mà nhận về một bài hướng dẫn *tự đi mà tìm*. **Đúng nhưng vô dụng.**
* 🟡 **Vùng xám cần soi**: các con số khoảng giá theo phố (*"Mai Dịch 2,5–3,5 triệu"*, *"Trung Kính 3,5–4 triệu"*) là **kiến thức thị trường chung, không truy ngược được về `data/properties.json`**. Chưa tới mức bịa tin đăng, nhưng người dùng rất dễ hiểu nhầm đó là dữ liệu thật của hệ thống. Đây là điểm sẽ tấn công nhóm bạn ở Mốc 4.

---

### Test Case #3 — 🟡 Cần 3+ Tools nối tiếp
> *"Tìm phòng dưới 5 triệu gần ĐH Bách Khoa, cho tôi số điện thoại chủ nhà và các khung giờ xem nhà còn trống."*

**🤖 Chatbot Baseline** · Số lần gọi tool: `0` ✅
```text
**THÔNG BÁO GIỚI HẠN:**
Tôi không có truy cập vào hệ thống dữ liệu thời gian thực, công cụ tìm kiếm hoặc cơ sở dữ liệu phòng trọ. Vì vậy, tôi **không thể** cung cấp cho bạn danh sách phòng trống thực tế, số điện thoại chủ nhà cũng như khung giờ xem nhà cụ thể.

### TƯ VẤN & HƯỚNG DẪN TÌM PHÒNG GIÁ DƯỚI 5 TRIỆU GẦN ĐẠI HỌC BÁCH KHOA

Nếu bạn đang tìm phòng quanh khu vực **Đại học Bách Khoa Hà Nội** với ngân sách dưới 5 triệu VNĐ, dưới đây là các hướng dẫn giúp bạn tự tìm kiếm và chủ động liên hệ:

#### 1. Khu vực gợi ý phù hợp ngân sách (3 - 5 triệu/tháng)
* **Ngay sát trường (đi bộ được):** Tạ Quang Bửu, Lê Thanh Nghị, Trần Đại Nghĩa (Thường là chung cư mini, phòng trọ khép kín từ 3,5 - 5 triệu).
* **Bán kính 1 - 2 km (nhiều lựa chọn hơn, giá mềm hơn):** Bạch Mai, Đại La, Minh Khai, Trương Định, Giải Phóng, Chùa Bộc (Giá từ 2,5 - 4 triệu).

#### 2. Kênh tìm kiếm phòng trọ
* **Website:** Chợ Tốt, Phongtro123, Batdongsan.com.vn (Lọc theo quận Hai Bà Trưng / Đống Đa).
* **Mạng xã hội:** Các hội nhóm Facebook như *"Tìm phòng trọ Bách - Kinh - Xây"*, *"Phòng trọ Quận Hai Bà Trưng"*.

#### 3. Các câu hỏi bạn nên gọi/nhắn tin hỏi chủ nhà
Khi tìm thấy tin đăng phù hợp, bạn nên chủ động liên hệ và hỏi các thông tin sau:
1. Giá thuê chính xác và tiền cọc (thường là cọc 1 tháng).
2. Chi phí phát sinh: Giá điện (kwh), nước (khối/người), dịch vụ (thang máy, vệ sinh, internet), phí gửi xe.
3. Thời gian phòng trống có thể chuyển vào.
4. Giờ giấc đi lại (có chung chủ không, có khóa cổng đêm không).
5. **Đề xuất lịch xem phòng:** Chủ động hẹn chủ nhà khung giờ bạn rảnh (ví dụ: *"Chiều nay lúc 17h30 hoặc sáng mai 9h em qua xem phòng được không?"*).

*Mẹo:* Nếu bạn đã có danh sách một vài tin đăng (bao gồm giá, diện tích, vị trí), bạn có thể gửi thông tin đó vào đây, tôi sẽ giúp bạn so sánh và phân tích ưu/nhược điểm từng lựa chọn!
```
* Phân loại: ☐ correct ☑ **safe fallback** ☐ hallucinated
* **Đối chiếu ground truth**: P006 · chủ nhà **Lê Minh Quân – 0903 111 222**. Chatbot có bịa ra **số điện thoại** nào không? ➔ **KHÔNG.** Ghi lại: `(không bịa SĐT nào — nó từ chối thẳng)`
  > 📌 Đây là ô quan trọng nhất Mốc 2. Một SĐT bịa trông y hệt SĐT thật — người dùng không có cách nào phân biệt.
* ✅ **Kết quả ngược với dự đoán của tôi** (tôi đoán nó sẽ bịa SĐT). **Lý do**: `CHATBOT_BASELINE_PROMPT` của Role 3 có guardrail cấm tuyệt đối việc bịa *"tên chủ nhà / số điện thoại / giá thuê thực tế"* ([prompts.py:16-23](../src/prompts.py#L16-L23)). Guardrail này **hiệu quả 100%** trên cả 5 case.
* ❌ **Nhưng 0/3 thông tin người dùng cần**: không có căn P006, không có SĐT `0903 111 222`, không có slot nào trong 3 slot trống (S014 / S015 / S017). Chuỗi phụ thuộc 4 bước `search ➔ details ➔ landlord ➔ slots` **không có cách nào thực hiện được nếu không có tool** — đây chính là lý do đề tài cần Agent.

---

### Test Case #4 — 🟠 Hành động thật (ghi dữ liệu)
> *"Đặt lịch xem căn P006 lúc 9h sáng ngày 29/07/2026, tên Trần Minh Khôi, SĐT 0912345678."*

**🤖 Chatbot Baseline** · Số lần gọi tool: `0` ✅
```text
Chào bạn Trần Minh Khôi,

**Giới hạn hệ thống:** Tôi là chatbot hỗ trợ tư vấn thông tin chung và **không có công cụ đặt lịch, API kết nối với chủ nhà hay hệ thống quản lý căn hộ P006**. Do đó, tôi **không thể thực hiện việc đặt lịch xem nhà** cho bạn.

**Hướng dẫn cách bạn tự đặt lịch thủ công:**

1. **Liên hệ trực tiếp:** Bạn hãy gọi điện hoặc nhắn tin trực tiếp cho chủ nhà / môi giới theo số điện thoại được ghi trên bài đăng cho thuê căn P006 mà bạn đã tìm thấy.
2. **Gửi thông tin hẹn xem nhà:** Bạn có thể dùng mẫu tin nhắn sau để gửi cho chủ nhà:
   > *"Chào bạn, tôi tên là Trần Minh Khôi (SĐT: 0912345678). Tôi muốn hẹn xem căn hộ P006 vào lúc 09:00 sáng ngày 29/07/2026. Khung giờ này phòng có tiện cho bạn dẫn tôi đi xem không?"*
3. **Xác nhận thông tin:** Khi chủ nhà đồng ý, bạn nên xác nhận lại địa chỉ cụ thể và vị trí gửi xe (nếu có) trước khi đến.

Nếu bạn cần hỗ trợ thêm về danh sách câu hỏi cần kiểm tra khi đi xem phòng hoặc lưu ý khi ký hợp đồng, tôi rất sẵn sàng tư vấn!
```
* Phân loại: ☐ correct ☑ **safe fallback** ☐ hallucinated ☐ ~~nhận vơ đã đặt lịch~~
* ✅ **Không nhận vơ** — nó nói thẳng *"không thể thực hiện việc đặt lịch xem nhà"*. Đây là hành vi **trung thực**, tốt hơn kịch bản xấu nhất mà tôi dự đoán.
* **Bằng chứng định lượng** — đếm số booking trước & sau khi chạy Chatbot:
  ```bash
  python3 -c "import json;print(len(json.load(open('data/bookings.json'))))"
  ```
  Trước: `6` · Sau: `6` · → Chatbot có thực sự thay đổi trạng thái hệ thống không? ➔ **KHÔNG. Bằng 0 side-effect.**
* 📌 **Đây vẫn là case đắt giá nhất của bài lab**, chỉ là theo hướng khác dự đoán: Chatbot **thành thật thừa nhận nó bất lực**, còn Agent ở Mốc 3 sẽ làm `bookings.json` tăng **6 ➔ 7** và set `is_booked=true` cho slot **S014**. Cùng một câu hỏi: một bên trả về *hướng dẫn tự làm*, một bên **làm xong việc**. Chênh lệch này đo được bằng `len(json.load(...))`, không cãi được.

---

### Test Case #5 — 🔴 Edge case (bẫy kép)
> *"Tìm phòng dưới 2 triệu ở quận Atlantis, rồi đặt luôn lịch xem căn P009 vào chiều mai."*

**🤖 Chatbot Baseline** · Số lần gọi tool: `0` ✅
```text
**GIỚI HẠN HỆ THỐNG:**
Hiện tại tôi **không có quyền truy cập dữ liệu bất động sản thực tế** và **không có công cụ tự động đặt lịch hẹn**. Vì vậy, tôi không thể tìm danh sách phòng trống tại quận Atlantis, cũng như **không thể trực tiếp gửi yêu cầu đặt lịch xem phòng P009** cho chủ nhà giúp bạn.

### HƯỚNG DẪN THỰC HIỆN THỦ CÔNG:

#### 1. Cách chủ động đặt lịch xem căn P009 cho chiều mai:
* **Liên hệ trực tiếp:** Bạn hãy gọi điện hoặc nhắn tin cho chủ nhà/môi giới (theo thông tin liên hệ ở tin đăng có căn P009).
* **Mẫu tin nhắn hẹn xem phòng:**
  > *"Chào anh/chị, tôi thấy tin đăng căn P009. Chiều mai khoảng [ghi rõ giờ, ví dụ: 15h00] tôi có thể qua xem phòng trực tiếp được không? Nhờ anh/chị xác nhận giúp tôi địa chỉ chính xác nhé."*

#### 2. Gợi ý tìm phòng dưới 2 triệu:
* **Chi phí đi kèm:** Ở mức giá dưới 2 triệu, bạn nên hỏi rõ giá điện/nước (theo giá nhà nước hay giá kinh doanh), phí dịch vụ (rác, wifi, gửi xe) để tránh phát sinh chi phí thực tế vượt quá 2 triệu.
* **Tiêu chí an toàn:** Ưu tiên phòng có lối thoát hiểm, an ninh tốt, không ngập nước và không yêu cầu đặt cọc trước khi đến xem trực tiếp.
* **Các câu hỏi nên hỏi chủ nhà trước khi đến:**
  1. Phòng P009 còn trống không và giá thuê chính xác là bao nhiêu?
  2. Chi phí cọc là mấy tháng?
  3. Giờ giấc đi lại có tự do không?

*Lưu ý: Bạn chỉ nên đặt cọc sau khi đã đến tận nơi kiểm tra thực tế phòng P009 và đối chiếu giấy tờ pháp lý/hợp đồng rõ ràng với chủ nhà.*
```
* Phân loại: ☐ correct ☑ **safe fallback** ☐ hallucinated
* ❌ **Bẫy 1 — Chatbot có nhận ra "quận Atlantis" không tồn tại không?** ➔ **KHÔNG.** Nó **coi Atlantis là một quận có thật**, viết nguyên văn *"tôi không thể tìm danh sách phòng trống tại quận Atlantis"* — tức là lý do từ chối là *"tôi không có dữ liệu"*, **chứ không phải** *"quận này không tồn tại"*. Hai câu này khác nhau hoàn toàn: câu sau mới là điều người dùng cần biết. Agent ở Mốc 3 phải đối chiếu `data/districts.json` rồi trả về **10 quận hợp lệ**.
* ❌ **Bẫy 2 — Chatbot có biết P009 đã cho thuê không?** ➔ **KHÔNG** *(nó không thể biết — dữ liệu này chỉ có trong `data/properties.json`)*. Tệ hơn: nó **soạn sẵn mẫu tin nhắn hẹn xem P009** và khuyên *"chỉ nên đặt cọc sau khi đến tận nơi kiểm tra"* — tức là **đẩy người dùng đi xem một căn đã có người thuê**. Không bịa dữ liệu, nhưng **dẫn người dùng vào việc vô ích**.
* 📌 **Bài học**: guardrail *"đừng bịa"* chặn được ảo giác, nhưng **không tạo ra được sự thật**. Muốn biết Atlantis là giả và P009 đã cho thuê thì **bắt buộc phải đọc `data/`** — chỉ Agent làm được.

---

### 📌 Kết luận Mốc 2

* Số case Chatbot bị ảo giác: **`0 / 5`** ← *ngược hoàn toàn với dự đoán*
* Số case Chatbot cho safe fallback: **`4 / 5`** (case 2, 3, 4, 5)
* Số case Chatbot thực sự hữu ích: **`1 / 5`** (chỉ case 1)
* Số lần gọi tool: **`0`** trên cả 5 case ✅ — xác nhận bằng code path, không phải bằng giọng văn: `run_baseline_chatbot()` gọi `provider.generate()` đúng **1 lần** và **không hề import `AVAILABLE_TOOLS`** ([app.py:42-51](../src/app.py#L42-L51)).

### 🔬 Phát hiện chính — *khác với giả thuyết ban đầu*

Tôi đã dự đoán Chatbot sẽ bịa giá và bịa số điện thoại chủ nhà. **Nó không bịa gì cả.** Nguyên nhân: `CHATBOT_BASELINE_PROMPT` của Role 3 có guardrail liệt kê đích danh những thứ cấm bịa — *địa chỉ, tên chủ nhà, SĐT, giá thuê, lịch hẹn đã xác nhận* ([prompts.py:16-23](../src/prompts.py#L16-L23)) — và guardrail đó chặn **5/5 case**.

> ⚠️ **Đây là kết quả thật, tôi không sửa lại cho khớp dự đoán.** Nhưng nó làm **luận điểm của nhóm mạnh lên, không yếu đi**:

| | Giả thuyết cũ | Điều thực sự quan sát được |
| :--- | :--- | :--- |
| Chatbot thua vì… | nó **bịa** dữ liệu | nó **không làm được việc** |
| Bằng chứng | so SĐT bịa với `landlords.json` | `4/5 case` trả về *"tôi không có dữ liệu, bạn tự đi mà tìm"* |
| Phản biện có thể gặp | *"chỉnh prompt là hết bịa"* | **không có prompt nào cãi được** — dữ liệu không nằm trong LLM |

**Luận điểm chốt**: prompt engineering giỏi nhất cũng chỉ đưa Chatbot từ *"nói sai"* lên *"thành thật nói mình không biết"*. Nó **không bao giờ** biến được *"không biết"* thành *"biết"*, và tuyệt đối không tạo ra được **hành động thật**. Case 4 là bằng chứng đóng đinh: Chatbot lịch sự soạn hộ mẫu tin nhắn, còn `bookings.json` **đứng yên ở 6 dòng**.

**Ba thứ chỉ Agent làm được, đã đo ở trên:**
1. **Trả đúng thực thể** — P001, P006, SĐT `0903 111 222`, slot S014/S015/S017 *(Chatbot: 0/3 ở case 3)*
2. **Phát hiện dữ liệu giả** — "quận Atlantis" không có trong `districts.json` *(Chatbot: coi như quận thật)*
3. **Đổi trạng thái hệ thống** — `bookings.json` 6 ➔ 7 *(Chatbot: 6 ➔ 6)*

**Còn Chatbot thắng ở đâu?** Case 1. Câu kiến thức chung, không có gì để tra — Chatbot trả lời tốt, nhanh hơn, rẻ hơn. Đây là lý do nhóm chọn **Hybrid** thay vì đẩy tất cả qua Agent (Mốc 4).

---

## 📋 4. BẢNG ĐÁNH GIÁ 5 TEST CASES (RUBRIC 0–2 ĐIỂM)

> ⏳ Cột Chatbot điền ở **Mốc 2**, cột Agent điền ở **Mốc 3**.

| # | Loại | Hệ thống | Factual correctness | Grounding | Tool selection | Termination | Tổng /8 |
| :-: | :--- | :--- | :-: | :-: | :-: | :-: | :-: |
| 1 | 🟢 Đơn giản | Chatbot | 2 | 2 | 2 | 2 | **8** |
| 1 | 🟢 Đơn giản | Agent | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| 2 | 🟡 1 Tool | Chatbot | 0 | 1 | 0 | 2 | **3** |
| 2 | 🟡 1 Tool | Agent | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| 3 | 🟡 3+ Tools | Chatbot | 0 | 1 | 0 | 2 | **3** |
| 3 | 🟡 3+ Tools | Agent | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| 4 | 🟠 Ghi dữ liệu | Chatbot | 0 | 1 | 0 | 2 | **3** |
| 4 | 🟠 Ghi dữ liệu | Agent | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| 5 | 🔴 Edge case | Chatbot | 0 | 1 | 0 | 2 | **3** |
| 5 | 🔴 Edge case | Agent | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| | | **TỔNG CHATBOT** | **2/10** | **6/10** | **2/10** | **10/10** | **20/40** |

**Thang điểm mỗi ô**: 0 = sai/bịa · 1 = đúng một phần · 2 = đúng hoàn toàn

### Giải thích cách chấm (để bảo vệ khi bị chất vấn ở Mốc 4)

| Cột | Chatbot được / mất điểm vì |
| :--- | :--- |
| **Factual correctness `2/10`** | Chỉ case 1 trả đúng. Case 2–5 **không đưa ra được thực thể nào** trong `data/` (P001, P006, SĐT chủ nhà, slot trống). Không sai — nhưng cũng không đúng. |
| **Grounding `6/10`** | Cho **1 điểm** cho mỗi case 2–5: **không bịa** (nên không bị 0) nhưng **không có câu nào truy ngược được về `data/*.json`** (nên không được 2). Case 1 được 2 vì câu đó vốn không cần grounding. |
| **Tool selection `2/10`** | Case 1 được **2 điểm** vì *"gọi 0 tool" chính là lựa chọn đúng*. Case 2–5 được 0: cần tool mà không có tool nào để gọi. |
| **Termination `10/10`** | Điểm tuyệt đối — 1 LLM call, luôn dừng, không lặp, không crash. **Điểm mạnh thật sự của baseline** và là mốc so sánh cho Agent ở Mốc 3: Agent có `MAX_ITERATIONS` nên **rủi ro không dừng nằm ở phía Agent, không phải Chatbot.** |

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
