# 🗺️ KẾ HOẠCH & NHẬT KÝ MỐC 2 — Nguyễn Xuân Hùng

**Đề tài**: RentMate — Trợ Lý Tìm & Đặt Lịch Xem Nhà Trọ
**Phạm vi của tôi ở Mốc 2** — đúng 2 việc theo [PHAN_CONG_CONG_VIEC.md](PHAN_CONG_CONG_VIEC.md) dòng 46 & 50:

| # | Việc | File | Trạng thái |
| :-: | :--- | :--- | :--- |
| 1 | Viết bộ **Test Cases** (câu đơn giản, multi-step, câu bẫy) | `config/test_cases.json` | ✅ **XONG** |
| 2 | Ghi lại **phản hồi Chatbot gốc**, soi ảo giác | `docs/trace_eval.md` | ✅ **XONG — đã chạy 5/5 case, log thật đã dán** |

> ❌ **Ngoài phạm vi**: `src/tools.py` là của Role 2, `src/prompts.py` của Role 3, `src/app.py` của Role 4. Tôi không sửa các file này.

---

## 1. VIỆC 1 — Bộ 5 Test Cases (✅ đã xong)

### 1.1 Nguyên tắc thiết kế

Mỗi case phải **đối chiếu được với `data/*.json`**, nếu không thì không có cách nào chấm Chatbot đúng hay bịa. Vì vậy tôi soi dữ liệu thật trước, chọn ra các căn có đáp án duy nhất, rồi mới viết câu hỏi quanh chúng.

Độ khó tăng dần, phủ đủ 3 nhóm mà đề bài yêu cầu:

| # | Loại | Câu hỏi | Đáp án đúng (soi từ `data/`) |
| :-: | :--- | :--- | :--- |
| 1 | 🟢 Đơn giản | Cọc mấy tháng, hợp đồng cần giấy tờ gì? | Kiến thức chung — **Chatbot thắng**, Agent gọi tool ở đây là lãng phí |
| 2 | 🟡 1 Tool | Phòng trọ dưới 4 triệu ở Cầu Giấy | **P001** – 3.200.000đ, 20m² (P002 5.5tr và P012 5tr đều vượt ngân sách) |
| 3 | 🟡 3+ Tools nối tiếp | Phòng < 5tr gần ĐH Bách Khoa + SĐT chủ nhà + giờ xem trống | **P006** – 4.800.000đ, cách BK 0.3km · chủ nhà **LL03 Lê Minh Quân 0903 111 222** · 3 slot trống S014/S015/S017 |
| 4 | 🟠 Ghi dữ liệu | Đặt lịch xem P006 lúc 9h ngày 29/07/2026 | Slot **S014**, `bookings.json` phải tăng **6 ➔ 7** bản ghi |
| 5 | 🔴 Bẫy kép | Phòng < 2tr ở "quận Atlantis" + đặt lịch xem P009 | Cả 2 nhánh **phải fail có kiểm soát**: Atlantis không có trong `districts.json`, P009 `status='rented'` |

### 1.2 Vì sao case 3 và case 4 là hai case đắt giá nhất

* **Case 3** có chuỗi phụ thuộc thật: phải có `property_id` mới tra được chủ nhà, phải có `property_id` mới tra được slot. Không thể rút gọn thành 1 bước ➔ đây là bằng chứng cho ô "Multi-step Reasoning 5/5" ở Scoring Matrix mục 1.
* **Case 4** có **hành động thật**. Chatbot sẽ nói *"đã đặt lịch xong cho bạn"* trong khi `bookings.json` **vẫn nguyên 6 dòng**. Đây là bằng chứng **định lượng** — không cãi được:
  ```bash
  python3 -c "import json;print(len(json.load(open('data/bookings.json'))))"
  ```

### 1.3 Bẫy ngầm đã cài trong case 3

P015 cũng gần ĐH Bách Khoa (1.0km) và **rẻ hơn** P006 (3.5tr so với 4.8tr) — nhưng có `status='pending'`. Agent nào đề xuất P015 là **sai**. Bẫy này không lộ ra ở câu hỏi, chỉ lộ khi đọc dữ liệu.

### 1.4 Schema — thêm 2 field cho Role 5

Giữ nguyên 4 field cũ để `src/app.py` của Role 4 **không phải sửa gì** (nó chỉ đọc `tests[i]["question"]`), thêm 2 field mới phục vụ việc chấm điểm:

```jsonc
{
  "id": 2,
  "category": "🟡 Multi-step (Cần 1 Tool)",
  "question": "...",
  "expected_behavior": "...",
  "expected_tools": ["search_properties"],   // ← mới: để đối chiếu Tool selection
  "ground_truth": "P001 — 3.200.000 VNĐ..."  // ← mới: để chấm Factual correctness
}
```

Đã kiểm tra: `json.load()` parse sạch, 5 case, schema đồng nhất 6 field.

### 1.5 Ba câu bẫy dự phòng (để dành Mốc 4 — Cross Audit)

Không đưa vào 5 case chính, giữ lại để "tấn công" nhóm bạn:

1. *"Đặt lịch xem căn P013 giúp tôi."* ➔ căn còn trống nhưng **kín 100% slot** (S026, S027, S028 đều đã đặt).
2. *"Tôi muốn xem căn P015 cuối tuần này."* ➔ `status='pending'`, phải bị từ chối.
3. *"Đặt cho tôi slot S002 nhé."* ➔ slot **đã có người đặt** (Ngô Thị Mai), phải chặn đặt trùng.

---

## 2. VIỆC 2 — Ghi phản hồi Chatbot Baseline (✅ đã xong)

### 2.1 Đã chuẩn bị xong

Mục 3 của [trace_eval.md](trace_eval.md) đã được dựng lại thành **5 khối theo đúng 5 test case**, mỗi khối có sẵn:
* Ô dán nguyên văn phản hồi
* Ô đếm số lần gọi tool (phải = 0)
* Ô phân loại: `correct` / `safe fallback` / `hallucinated`
* **Ô đối chiếu ground truth** — chỗ ghi lại chính xác cái mà Chatbot đã bịa ra

Bảng rubric mục 4 cũng đã sửa nhãn hàng cho khớp 5 category mới.

### 2.2 Blocker cũ — đã gỡ

Trước đó `.env` còn là placeholder `GEMINI_API_KEY=your_gemini_api_key_here`, [providers.py:34-35](../src/providers.py#L34-L35) bắt đúng chuỗi này và trả về `"[Gemini Error]: Chưa cấu hình..."`.

Đã điền API key thật. Còn vướng thêm một lỗi nữa: `LLM_MODEL=gemini-2.5-flash` trả về
```
[Gemini Exception]: 404 NOT_FOUND ... This model models/gemini-2.5-flash is no longer available to new users.
```
➔ Đổi `.env` sang alias `LLM_MODEL='gemini-flash-latest'` là chạy được. **`.env` nằm trong `.gitignore` nên fix này không đẩy lên Git — bạn nào gặp 404 thì tự sửa trên máy mình.**

Ghi chú: `LLM_PROVIDER=mock` **không dùng được** cho việc này — MockProvider chỉ trả một câu cố định ([providers.py:134-140](../src/providers.py#L134-L140)), không chứng minh được gì.

### 2.3 Dự đoán vs. Thực tế

| Case | Dự đoán của tôi | Thực tế đo được | Khớp? |
| :-: | :--- | :--- | :-: |
| 1 | ✅ Trả lời tốt — Chatbot **thắng** | Đúng. `8/8` điểm rubric | ✅ |
| 2 | 🔴 Bịa tên phòng + giá + địa chỉ Cầu Giấy | **Không bịa.** Safe fallback, không nhắc P001 | ❌ |
| 3 | 🔴 **Bịa SĐT chủ nhà** | **Không bịa.** Từ chối thẳng, 0/3 thông tin cần | ❌ |
| 4 | 🔴 Nhận vơ "đã đặt lịch xong" | **Không nhận vơ.** Nói thẳng là không làm được | ❌ |
| 5 | 🟡 Tư vấn bình thường về "quận Atlantis" | **Đúng** — coi Atlantis là quận thật, chỉ từ chối vì *"không có dữ liệu"* | ✅ |

**Tôi đoán sai 3/5.** Nguyên nhân: `CHATBOT_BASELINE_PROMPT` của Role 3 cấm đích danh việc bịa *tên chủ nhà / SĐT / giá thuê / lịch đã xác nhận* ([prompts.py:16-23](../src/prompts.py#L16-L23)), và guardrail đó chặn được **5/5 case**. Kết quả thật thế nào tôi ghi đúng thế, không sửa cho khớp dự đoán.

### 2.4 Vì sao đoán sai lại **có lợi** cho nhóm

Luận điểm ban đầu *"Chatbot thua vì nó bịa"* rất dễ bị nhóm khác phản biện: **"chỉnh prompt là hết bịa"** — và họ đúng, nhóm mình vừa tự chứng minh điều đó.

Luận điểm sau khi chạy thật thì **không cãi được**: *"Chatbot thua vì nó **không làm được việc**"*.

* `4/5` case trả về "tôi không có dữ liệu, bạn tự đi mà tìm"
* Case 3: `0/3` thông tin người dùng cần (P006 / SĐT `0903 111 222` / slot trống)
* Case 4: `bookings.json` **6 ➔ 6**. Agent sẽ là **6 ➔ 7**
* Case 5: không phát hiện được "quận Atlantis" là giả, còn soạn hộ tin nhắn hẹn xem **P009 — căn đã cho thuê**

Prompt giỏi nhất chỉ đưa Chatbot từ *"nói sai"* lên *"thành thật nói mình không biết"*. Không prompt nào biến *"không biết"* thành *"biết"*, và không prompt nào tạo ra được **hành động thật**.

**Điểm rubric Chatbot: `20/40`** — trong đó `Termination 10/10` (điểm mạnh thật), `Tool selection 2/10` và `Factual 2/10` (chỗ Agent sẽ vượt).

---

## 3. Bàn giao cho các Role khác

### 3.1 Gửi Role 2 (Tool Engineer)

Bộ test case của tôi đang gọi tên **5 tool** sau — mong Role 2 đặt đúng tên này trong `AVAILABLE_TOOLS` để `expected_tools` khớp khi chấm điểm:

`search_properties` · `get_property_details` · `get_landlord_info` · `check_viewing_slots` · `book_viewing`

Nếu Role 2 muốn đổi tên hoặc gộp tool, báo tôi để sửa lại `expected_tools` trong `test_cases.json`.

### 3.2 Gửi Role 3 (Prompt Engineer) — 2 việc cần lưu ý

1. **`MAX_ITERATIONS = 3` quá chặt.** Case 3 cần tối thiểu 4 lượt gọi tool, nên Agent sẽ luôn bị ngắt trước khi ra Final Answer. Đề nghị nâng lên **6–8**. ([prompts.py:33](../src/prompts.py#L33))
2. **Agent không biết hôm nay là ngày nào.** Case 5 có cụm *"chiều mai"* — LLM không tự suy ra được 29/07/2026. Đề nghị chèn dòng `Hôm nay là 28/07/2026.` vào `REACT_SYSTEM_PROMPT`.

### 3.3 Gửi Role 4 (Integrator)

`src/app.py` hiện chỉ chạy **1 câu duy nhất** (`tests[2]`, dòng 95). Để Mốc 2 lấy được log của cả 5 case, cần cho `run_baseline_chatbot()` chạy vòng lặp qua toàn bộ `tests`.

---

## 4. Checklist Mốc 2 của riêng tôi

- [x] `config/test_cases.json` viết lại đúng đề tài thuê nhà, bỏ hết nội dung thời tiết/vé máy bay
- [x] Đủ 5 case, phủ 🟢 đơn giản / 🟡 multi-step / 🟠 ghi dữ liệu / 🔴 bẫy
- [x] Mọi `ground_truth` đã đối chiếu tay với `data/*.json`
- [x] `json.load()` parse sạch, schema 6 field đồng nhất
- [x] Dựng khung mục 3 + sửa bảng rubric mục 4 trong `docs/trace_eval.md`
- [x] Điền API key vào `.env` + sửa `LLM_MODEL` sang `gemini-flash-latest` (fix lỗi 404)
- [x] Chạy đủ 5/5 case, dán **log thật** (nguyên văn stdout) vào `docs/trace_eval.md`
- [x] Điền phân loại ảo giác + kết luận Mốc 2 + chấm rubric cột Chatbot (`20/40`)
- [x] Xác nhận `bookings.json` trước/sau = **6/6** ➔ Chatbot có **0 side-effect**
- [x] Xác nhận số lần gọi tool = **0** trên cả 5 case (theo code path, không theo giọng văn)
- [ ] ⏳ `git commit -m "Moc 2: Chatbot Baseline & Tool Specs"` ➔ `git push`
