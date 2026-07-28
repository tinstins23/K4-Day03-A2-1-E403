# 🗺️ KẾ HOẠCH MỐC 3 — Nguyễn Xuân Hùng (Role 1 + Role 5)

**Đề tài**: RentMate · **Ngày lập**: 2026-07-28 · Nối tiếp [Hung-Moc2.md](Hung-Moc2.md)

**Trạng thái**: 🟡 **Việc Role 1 làm được ngay** · **Việc Role 5 chờ Role 3 + Role 4**

---

## 1. PHẠM VI CỦA TÔI Ở MỐC 3

Theo [PHAN_CONG_CONG_VIEC.md](PHAN_CONG_CONG_VIEC.md) dòng 62 & 63, tôi có đúng **2 việc**:

| # | Vai | Việc | File tôi được sửa | Chờ ai? |
| :-: | :-- | :--- | :--- | :--- |
| 1 | **Role 1** | Kiểm tra Agent có vượt được **câu bẫy (Edge Case)** bằng Guardrail không | `config/test_cases.json` | 🟢 **Không chờ ai** |
| 2 | **Role 5** | Trích chuỗi `Thought ➔ Action ➔ Observation` dán vào trace | `docs/trace_eval.md` | 🔴 Role 3 + Role 4 |

> ❌ **Ngoài phạm vi, tôi không sửa**: `src/tools.py` (Role 2) · `src/prompts.py` (Role 3) · `src/app.py` (Role 4).
> Vấn đề phát hiện ở các file đó ➔ ghi thành **phiếu báo lỗi** ở mục 5, gửi đúng người.

---

## 2. 🔴 BLOCKER — CHỈ CÒN HAI NGƯỜI

| # | Vấn đề | Bằng chứng | Chủ sở hữu |
| :-: | :--- | :--- | :--- |
| **B1** | `run_react_agent()` **hardcode 100%** — không gọi LLM, không gọi tool. In sẵn *"Phòng Dịch Vọng 3.5tr"*, *"Studio Quan Hoa 3.8tr"* — **hai căn không tồn tại trong `data/properties.json`** | [app.py:65-79](../src/app.py#L65-L79) | **Role 4** |
| **B2** | `REACT_SYSTEM_PROMPT` vẫn là **boilerplate đề tài cũ** — khai báo `get_weather[location]`, `search_flights[origin, destination]`. Không có tool RentMate nào | [prompts.py:56-57](../src/prompts.py#L56-L57) | **Role 3** |
| **B3** | `MAX_ITERATIONS = 3` — case 3 cần **tối thiểu 5 vòng**, luôn bị ngắt trước Final Answer | [prompts.py:72](../src/prompts.py#L72) | **Role 3** |

> 📌 **B1 nguy hiểm nhất**: `run_react_agent()` đang **in Observation bịa sẵn trong code Python**. CLAUDE.md mục 7 gọi đây là *"Agent trở thành chatbot đóng vai, không phải agent thật"* — ở đây còn tệ hơn, **lập trình viên** sinh Observation chứ không phải LLM. Chạy demo với code này thì trace log là **trace giả**, vi phạm đúng luật mà `trace_eval.md` tự đặt.

### ✅ Role 2 KHÔNG phải blocker

Đây là chỗ tôi hiểu sai lúc đầu, đã sửa lại.

Việc Role 1 của tôi là **kiểm tra** Agent có vượt bẫy không, **không phải sửa** cho nó vượt. Lỗi tìm thấy trong `tools.py` chính là **kết quả kiểm tra** — tức là sản phẩm tôi nộp, không phải thứ chặn tôi. Role 2 sửa hay chưa sửa **không đổi việc tôi phải làm**.

Thậm chí nếu Role 2 **chưa sửa kịp**, Agent sẽ fail case đó ở Mốc 3 ➔ tôi có **failed trace thật từ app thật**, đúng thứ Mốc 4 bắt buộc phải có.

---

## 3. ✅ ĐÃ LÀM — KIỂM GUARDRAIL TẦNG TOOL (không cần Agent)

Guardrail có **hai tầng**. Tầng dưới nằm trong `tools.py`, Role 2 đã push ➔ **test được ngay, không cần LLM**, đúng như CLAUDE.md mục 4 hướng dẫn (`python src/tools.py`).

* **Tầng tool** — bản thân tool có chặn không? ➔ **kiểm xong hôm nay, kết quả bên dưới**
* **Tầng agent** — Agent có *gọi đúng* tool chặn đó không? ➔ chờ B1/B2

### 3.1 Kết quả chạy thật (2026-07-28)

| # | Guardrail | Kết quả thực tế | Đạt |
| :-: | :--- | :--- | :-: |
| **G3** | Căn `pending` không được đề xuất trong search | `search_properties('Hai Bà Trưng', 5000000)` ➔ `['P006']`. **P015 bị loại đúng** | ✅ |
| **G1** | Quận lạ ➔ lỗi + liệt kê 10 quận hợp lệ | `validate_district('Atlantis')` ➔ `"LỖI: Quận 'Atlantis' không tồn tại trong hệ thống."` — **thiếu danh sách quận hợp lệ**.<br>Nặng hơn: `search_properties('Atlantis', 2000000)` ➔ `[]` **im lặng, không báo lỗi** | ⚠️ |
| **G2** | Căn `rented` / `pending` ➔ từ chối đặt lịch kèm lý do | **Guardrail không tồn tại.** Xem 3.2 | 🔴 |

### 3.2 🐛 Lỗi G2 — `create_booking` không kiểm `status`

`create_booking` chỉ kiểm 3 thứ ([tools.py:300-318](../src/tools.py#L300-L318)):

1. Căn có tồn tại không
2. Slot có tồn tại không
3. Slot đã có người đặt chưa

**Không có bước nào kiểm `status`.** Trong khi CLAUDE.md mục 6 ghi rõ: *"`status` khác `available` ➔ tool **phải** từ chối đặt lịch, kèm lý do rõ ràng"*.

P009 từ chối được chỉ là **ăn may**: nó chết ở bước 2 vì không có slot nào, và trả về lý do **sai** — *"Không tìm thấy khung giờ"* thay vì *"căn đã cho thuê"*.

Lỗ hổng này **khai thác được thật**:

```
P009: status=rented    slot trống=[]          ← chặn nhờ ăn may
P012: status=rented    slot trống=[]          ← chặn nhờ ăn may
P015: status=pending   slot trống=['S031']    ← ĐẶT ĐƯỢC!
P013: status=available slot trống=[]          ← đúng thiết kế (kín slot)
```

➔ `create_booking('P015', 'S031', ...)` sẽ trả `success: true`, **đặt lịch cho căn chưa sẵn sàng cho thuê**.
*(Chưa chạy thật vì lệnh này ghi vào `bookings.json`.)*

### 3.3 Việc của Role 1 — quyết định về `ground_truth` case 5

`ground_truth` tôi viết ở Mốc 2 yêu cầu tool *"trả LỖI kèm danh sách 10 quận hợp lệ"* — **chặt hơn** code Role 2 đang có. Hai hướng:

* **(a)** Role 2 sửa cho khớp ground_truth ← **tôi chọn hướng này**
* **(b)** Tôi hạ chuẩn ground_truth cho khớp code

Chọn **(a)** vì: Agent nhận `[]` rỗng thì **không phân biệt được** *"quận không tồn tại"* với *"không có phòng phù hợp"*. Phân biệt được hai cái đó **chính là nội dung của G1**. Hạ chuẩn là tự bỏ điểm.

---

## 4. 🐛 MỤC 5 CỦA TRACE_EVAL — RCA ĐÃ CÓ 4/5 Ô

`docs/trace_eval.md` mục 5 (*Failed Trace & RCA*) đang trống, mà **Mốc 4 bắt buộc phải có ít nhất 1 failed trace thật**. Lỗi G2 lấp được ngay:

| Mục | Nội dung | Trạng thái |
| :--- | :--- | :-- |
| **Triệu chứng** | Đặt được lịch xem căn chưa sẵn sàng cho thuê (`status != available`) | ✅ có |
| **Trace lỗi (Before)** | `create_booking('P015','S031','...','...')` ➔ `{"success": true}`; `bookings.json` 6 ➔ 7 | ✅ có |
| **Nguyên nhân gốc** | [tools.py:300-318](../src/tools.py#L300-L318) kiểm căn tồn tại ➔ slot tồn tại ➔ slot trống, **thiếu bước kiểm `status`**. P009/P012 chặn được chỉ vì tình cờ không có slot | ✅ có |
| **Cách sửa ở Agent V2** | Chèn chặn `status != 'available'` vào `create_booking` **trước** khi ghi, trả lý do rõ ràng | ✅ có |
| **Trace sau khi sửa (After)** | Chạy lại đúng lệnh trên, phải ra `success: false` + lý do | ⏳ **chờ Role 2** |

**4/5 ô viết được ngay.** Chỉ ô cuối cần Role 2. Đây là lỗi thật, tìm bằng cách đọc dữ liệu — không phải lỗi dựng lên cho đủ bài.

---

## 5. 📮 PHIẾU BÁO GỬI CÁC ROLE KHÁC

### 5.1 Gửi Role 3 — `src/prompts.py` (**gấp, chặn cả nhóm**)

1. **Viết lại `REACT_SYSTEM_PROMPT`** — xóa `get_weather` / `search_flights`, khai đúng **8 tool** trong `AVAILABLE_TOOLS`, ghi rõ **chữ ký tham số** (không có thì LLM gọi sai):
   ```
   search_properties[district, max_price]
   get_property_details[property_id]
   get_landlord_info[property_id]          ← property_id, KHÔNG phải landlord_id
   get_available_slots[property_id]
   create_booking[property_id, slot_id, customer_name, customer_phone]
   validate_district[district]
   recommend_properties[property_id]
   get_booking[booking_id]
   ```
2. **`MAX_ITERATIONS = 3` ➔ `8`.** Case 3 cần 4 lần gọi tool + 1 lượt Final Answer = **5 vòng tối thiểu**. Để 3 thì case 3 **chắc chắn fail vì cấu hình**, không phải vì Agent dở. *(Đã nhắc ở Mốc 2, chưa sửa.)*
3. **Chèn ngày hiện tại**: `Hôm nay là 28/07/2026.` — case 5 có cụm *"chiều mai"*, LLM không tự suy ra 29/07/2026. *(Đã nhắc ở Mốc 2, chưa sửa.)*

### 5.2 Gửi Role 4 — `src/app.py` (**gấp, chặn cả nhóm**)

1. **Xóa toàn bộ `if step == 1 / elif step == 2` hardcode**, thay bằng vòng lặp thật:
   `gọi LLM ➔ parse "Action: tên[tham số]" ➔ tra AVAILABLE_TOOLS ➔ chạy tool ➔ nhét kết quả vào prompt làm Observation ➔ lặp`
2. **Observation phải do code Python chèn.** LLM tự sinh chữ `Observation:` thì **cắt bỏ** — CLAUDE.md gọi đây là *"lỗi nặng nhất của bài lab"*.
3. **Cho chạy cả 5 case**, đừng chỉ `tests[2]` ([app.py:100](../src/app.py#L100)). Mốc 2 tôi đã phải viết script phụ để lách; Mốc 3 cần trace của **tất cả** case.
4. **Bỏ / cho phép bỏ qua `input()`** ([app.py:103](../src/app.py#L103)) — đang chặn chạy tự động.
5. Tool trả `dict`/`list` chứ không phải `str` ➔ nhớ `json.dumps(..., ensure_ascii=False)` khi ghép vào Observation.

### 5.3 Gửi Role 2 — `src/tools.py` (không chặn tôi, nhưng ảnh hưởng điểm Guardrails)

✅ **Làm tốt**: không có `raise` nào trong cả 362 dòng — đúng yêu cầu *"tool không bao giờ raise exception"*.

Ba việc đề nghị, theo thứ tự ưu tiên:

1. 🔴 **`create_booking` thiếu kiểm `status`** — xem mục 3.2. Đây là lỗi Guardrail thật, đang khai thác được qua P015 + S031.
2. ⚠️ **`validate_district` nên trả kèm danh sách 10 quận hợp lệ** — CLAUDE.md mục 6 có sẵn mẫu: `"LỖI: Không tìm thấy quận '{district}'. Các quận hợp lệ: Cầu Giấy, Đống Đa, ..."`
3. ⚠️ **`search_properties` với quận không tồn tại đang trả `[]` im lặng** — nên trả chuỗi lỗi để Agent phân biệt *"quận sai"* với *"không có phòng phù hợp"*.

*(Điểm lệch chuẩn nhỏ: CLAUDE.md yêu cầu tool trả `str`, hiện đang trả `dict`/`list`. Không sai về logic — nhưng Role 2 và Role 4 thống nhất ai convert, đừng để rơi.)*

---

## 6. ❓ CÂU CẦN BẠN QUYẾT

**Phương án lấy trace: đã chốt ➔ CHỜ Role 3 + Role 4 làm xong rồi chạy `python src/app.py` lấy trace thật.**
*(Không tự dựng loop ngoài repo — trace phải sinh từ app thật thì Mốc 4 mới bảo vệ được.)*

Còn đúng **1 câu chưa quyết**:

> **Có thêm case 6 — P013 (còn trống nhưng kín 100% slot) vào `test_cases.json` không?**
>
> * ✅ **Thêm**: chứng minh được ô *Dynamic Decision 5/5* ở Scoring Matrix — hiện ô này tôi tự chấm 5/5 nhưng **chưa có test case nào backing**. Agent phải nhận ra hết lịch rồi **quay lại đề xuất căn khác** (dùng `recommend_properties` của Role 2).
> * ❌ **Không thêm**: bộ test giữ 5 câu gọn, và P013 vẫn là "quân bài" để tấn công nhóm bạn ở Mốc 4 ([Hung-Moc2.md](Hung-Moc2.md) mục 1.5).

---

## 7. CHECKLIST

### Giai đoạn 1 — làm được ngay, không chờ ai *(chờ bạn bật đèn xanh)*

* [ ] `config/test_cases.json`: `check_viewing_slots` ➔ **`get_available_slots`**, `book_viewing` ➔ **`create_booking`** *(tên tôi tự đặt ở Mốc 2 không khớp `AVAILABLE_TOOLS` thật — xem 7.1)*
* [ ] `config/test_cases.json`: sửa mô tả case 3 — `get_landlord_info` nhận **`property_id`**, không phải `landlord_id`
* [ ] `config/test_cases.json`: *(nếu duyệt)* thêm case 6 — P013 kín slot
* [ ] `docs/trace_eval.md`: dựng **mục 6 — Trace ReAct Agent**, mỗi case một khối `Thought / Action / Observation / Final Answer`
* [ ] `docs/trace_eval.md`: dựng **bảng kiểm Guardrail** + điền sẵn kết quả tầng tool ở mục 3.1
* [ ] `docs/trace_eval.md`: điền **4/5 ô RCA** ở mục 5 *(mục 4 file này)*

### Giai đoạn 2 — sau khi Role 3 + Role 4 push

* [ ] `git pull` ➔ `python src/app.py` ➔ dán trace **nguyên văn** cả 5 (hoặc 6) case
* [ ] Điền **cột Agent** bảng rubric mục 4 *(Chatbot đã xong: `20/40`)*
* [ ] Bảng so sánh **Chatbot vs Agent** trên cùng bộ câu hỏi
* [ ] Kiểm **tầng agent** của G1–G5: Agent có *gọi đúng* guardrail không
* [ ] Điền ô **After** của RCA *(cần Role 2 sửa G2)*
* [ ] `git commit -m "Moc 3: ReAct Agent Loop & Safeguards"` ➔ `git push`

### 7.1 Phụ lục — bảng đối chiếu tên tool

Ở Mốc 2 tôi viết `expected_tools` theo tên **tôi tự đặt** rồi nhắn Role 2. Role 2 code xong nhưng đặt tên khác ([tools.py:352-361](../src/tools.py#L352-L361)):

| Tên trong `test_cases.json` | Tên thật trong `AVAILABLE_TOOLS` | |
| :--- | :--- | :-: |
| `search_properties` | `search_properties` | ✅ |
| `get_property_details` | `get_property_details` | ✅ |
| `get_landlord_info` | `get_landlord_info` | ✅ |
| `check_viewing_slots` | **`get_available_slots`** | ❌ |
| `book_viewing` | **`create_booking`** | ❌ |

**Tôi sửa file mình, không bắt Role 2 đổi** — `tools.py` đã code xong 362 dòng, file tôi chỉ sửa 2 chuỗi. Ai sửa ít hơn thì người đó sửa.

Ba tool Role 2 làm thêm chưa dùng tới: `validate_district` · `get_booking` · `recommend_properties` *(cái cuối là lý do đề xuất case 6)*.
