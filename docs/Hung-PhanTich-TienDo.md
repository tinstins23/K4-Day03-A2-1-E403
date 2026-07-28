# 📊 PHÂN TÍCH TIẾN ĐỘ NHÓM — AI THIẾU VIỆC GÌ

**Người lập**: Nguyễn Xuân Hùng (Role 1 + Role 5) · **Ngày**: 2026-07-28
**Cách lập**: đọc `git log` toàn bộ branch + kiểm code thật, **không đoán**

---

## 1. 🚨 HAI PHÁT HIỆN QUAN TRỌNG NHẤT

### 1.1 Role 3 **ĐÃ LÀM XONG MỐC 3** — nhưng đang kẹt ở branch riêng

```
origin/NguyenManhThang  ➔  25a32ba  "Moc 3: ReAct Agent Loop & Safeguards"
```

Commit này **chưa merge vào `main`**, nên chưa ai thấy. Nội dung đã kiểm:

| Việc | Trạng thái |
| :--- | :-- |
| Xóa boilerplate `get_weather` / `search_flights` | ✅ sạch (0 dấu vết) |
| Khai báo đủ **8 tool** RentMate trong `REACT_SYSTEM_PROMPT` | ✅ đủ cả 8 |
| `MAX_ITERATIONS` 3 ➔ **6** | ✅ đủ cho case 3 (cần ≥5) |
| Chèn *"Hôm nay là 28/07/2026"* | ❌ **chưa có** |

➔ **Hai trong ba blocker tôi ghi ở [Hung-Moc3.md](Hung-Moc3.md) đã được gỡ.** Chỉ cần merge.

### 1.2 Role 4 đã viết `run_all_test_cases()` rồi **tự xóa đi**

Commit `4b1b15e` tên *"revert"* của TrungTin **gỡ bỏ 47 dòng**, trong đó có nguyên hàm:

```python
def run_all_test_cases(provider):
    """Chạy tự động toàn bộ bộ Test Cases từ config/test_cases.json..."""
```

Đây **đúng thứ tôi xin ở phiếu báo 5.2 mục 3** — chạy cả 5 case thay vì chỉ `tests[2]`. Nó đã tồn tại, rồi bị revert.

➔ Nên hỏi Role 4: *revert vì lỗi gì?* Nếu chỉ lỗi vặt thì khôi phục nhanh hơn viết lại.

⚠️ **Nhưng lưu ý**: kể cả trước khi revert, `run_react_agent()` **vẫn hardcode**. Batch runner chỉ chạy vòng lặp giả 5 lần. Việc chính của Role 4 vẫn còn nguyên đó.

---

## 2. 👥 AI LÀ AI (suy ra từ `git log`)

| Role | File | Người | Branch |
| :--- | :--- | :--- | :--- |
| **Role 1** Product Architect | `config/test_cases.json` | **Hùng (tôi)** | `NguyenXuanHung` |
| **Role 2** Tool Engineer | `src/tools.py` | **Quan Hoang** | `feature/quan` |
| **Role 3** Prompt Engineer | `src/prompts.py` | **ThangG** | `NguyenManhThang` |
| **Role 4** Integrator | `src/app.py` | **TrungTin** | `tin` |
| **Role 5** Observability | `docs/trace_eval.md` | **Hùng (tôi)** | `NguyenXuanHung` |

*(`kag2002` là người dựng boilerplate ban đầu, không phải thành viên nhóm.)*

---

## 3. 📋 BẢNG TỔNG — AI THIẾU GÌ

Ký hiệu: ✅ xong · 🟡 xong một nửa · ❌ chưa làm · ⏳ bị chặn bởi người khác

| Role | Mốc 1 | Mốc 2 | Mốc 3 | Việc còn thiếu |
| :--- | :-: | :-: | :-: | :--- |
| **1** Hùng | ✅ | ✅ | 🟡 | Sửa tên tool sai trong `test_cases.json` |
| **2** Quan | ✅ | 🟡 | 🟡 | Docstring thiếu mục · **3 lỗi Guardrail** |
| **3** Thắng | ⚠️ | ✅ | ✅ | **Merge vào main** · thiếu dòng ngày |
| **4** Tín | ✅ | 🟡 | ❌ | 🔴 **ReAct loop — chặn cả nhóm** |
| **5** Hùng | ✅ | ✅ | ⏳ | Chờ Role 4 |

---

## 4. 🔍 CHI TIẾT TỪNG ROLE

### 🟢 Role 1 — Hùng (tôi) · `config/test_cases.json`

| Mốc | Yêu cầu | Trạng thái |
| :-: | :--- | :-- |
| 1 | Chọn đề tài | ✅ RentMate |
| 2 | Viết test cases (đơn giản / multi-step / bẫy) | ✅ 5 case, có `ground_truth` đối chiếu tay với `data/` |
| 3 | Kiểm Agent vượt bẫy bằng Guardrail | 🟡 **xong tầng tool**, chờ Role 4 cho tầng agent |

**Còn thiếu — làm được ngay:**
1. `check_viewing_slots` ➔ **`get_available_slots`**
2. `book_viewing` ➔ **`create_booking`**
3. Case 3: `get_landlord_info` nhận **`property_id`**, không phải `landlord_id`

*(Tên tôi tự đặt ở Mốc 2 không khớp `AVAILABLE_TOOLS` thật của Role 2.)*

---

### 🟡 Role 2 — Quan · `src/tools.py`

| Mốc | Yêu cầu | Trạng thái |
| :-: | :--- | :-- |
| 1 | Liệt kê tên tool | ✅ 8 tool |
| 2 | Bổ sung docstring chuẩn | 🟡 **thiếu mục** |
| 3 | Tool gặp lỗi trả chuỗi, không crash | ✅ **0 lệnh `raise`** trong 362 dòng |

**Làm tốt**: không có `raise` nào — đúng yêu cầu quan trọng nhất của Mốc 3.

**Còn thiếu — xếp theo mức nghiêm trọng:**

**🔴 1. `create_booking` KHÔNG GHI XUỐNG ĐĨA** *(nặng nhất)*

`tools.py` **không có một lệnh ghi file nào** — chỉ `BOOKINGS.append()` vào list trong bộ nhớ rồi mất khi tắt chương trình.

```
create_booking(...) ➔ {"success": true, "message": "Đặt lịch thành công."}
data/bookings.json trên đĩa  ➔  vẫn 6 dòng
```

Đây là thứ phá **bằng chứng định lượng chủ lực của cả bài lab**. CLAUDE.md mục 5 ghi rõ `bookings.json` là *"file duy nhất bị GHI"*. Không sửa thì Chatbot 6→6, Agent cũng 6→6 — **mất luôn điểm so sánh mạnh nhất**.

**🔴 2. `create_booking` không kiểm `status`**

Chỉ kiểm 3 thứ: căn tồn tại ➔ slot tồn tại ➔ slot chưa ai đặt. **Thiếu bước kiểm `status`.**

```
P015: status=pending, slot S031 còn trống  ➔  ĐẶT LỊCH ĐƯỢC
```

P009/P012 chặn được chỉ vì **tình cờ hết slot**, và trả lý do sai (*"Không tìm thấy khung giờ"* thay vì *"căn đã cho thuê"*). CLAUDE.md mục 6: *"`status` khác `available` ➔ tool **phải** từ chối đặt lịch, kèm lý do rõ ràng"*.

**⚠️ 3. Quận không tồn tại báo lỗi chưa đủ**

* `validate_district('Atlantis')` ➔ `"LỖI: Quận 'Atlantis' không tồn tại trong hệ thống."` — **thiếu danh sách quận hợp lệ**
* `search_properties('Atlantis', 2000000)` ➔ `[]` **im lặng, không báo lỗi**

Agent nhận `[]` thì **không phân biệt được** *"quận không tồn tại"* với *"không có phòng phù hợp"*. CLAUDE.md có sẵn mẫu:
```python
return f"LỖI: Không tìm thấy quận '{district}'. Các quận hợp lệ: Cầu Giấy, Đống Đa, ..."
```

**⚠️ 4. Docstring thiếu mục**

CLAUDE.md mục 6 yêu cầu **8 mục**: tên · mục đích · input schema · output schema · **error semantics** · **side effect** · **ví dụ** · **an toàn**.

Hiện có `Args:` và `Returns:` đầy đủ (9/9 hàm), nhưng chỉ **2 hàm** có error semantics / ví dụ / an toàn.

**ℹ️ 5. Tool trả `dict`/`list` thay vì `str`** — không sai logic, nhưng Role 4 phải `json.dumps(..., ensure_ascii=False)` khi ghép vào Observation. Hai bạn thống nhất ai làm.

---

### ✅ Role 3 — Thắng · `src/prompts.py`

| Mốc | Yêu cầu | Trạng thái |
| :-: | :--- | :-- |
| 1 | Xác định Failure Modes của tool | ⚠️ không thấy tài liệu nào ghi lại |
| 2 | Soạn `CHATBOT_BASELINE_PROMPT` | ✅ **rất tốt** |
| 3 | `REACT_SYSTEM_PROMPT` + `MAX_ITERATIONS` | ✅ xong, **nhưng chưa merge** |

**Làm tốt nhất nhóm.** `CHATBOT_BASELINE_PROMPT` có guardrail cấm bịa *tên chủ nhà / SĐT / giá thuê* — tôi đã đo ở Mốc 2: **chặn được 5/5 case**, baseline không bịa gì cả.

**Còn thiếu:**
1. 🔴 **Merge `25a32ba` vào `main`** — việc đã xong mà cả nhóm chưa dùng được
2. ⚠️ Chèn `Hôm nay là 28/07/2026.` vào `REACT_SYSTEM_PROMPT` — case 5 có cụm *"chiều mai"*, LLM không tự suy ra 29/07/2026 *(tôi đã nhắc từ Mốc 2)*
3. ℹ️ Failure Modes (Mốc 1) chưa thấy ghi ở đâu — có thể đã bàn miệng

---

### 🔴 Role 4 — Tín · `src/app.py` — **ĐANG CHẶN CẢ NHÓM**

| Mốc | Yêu cầu | Trạng thái |
| :-: | :--- | :-- |
| 1 | Chạy `python src/app.py` kiểm tra môi trường | ✅ |
| 2 | `git pull` + nối `run_baseline_chatbot()` | 🟡 chạy được nhưng **chỉ 1 câu** |
| 3 | **Lắp vòng lặp ReAct hoàn chỉnh** | ❌ **chưa làm** |

**Vấn đề gốc**: `run_react_agent()` **hardcode 100%** ([app.py:65-79](../src/app.py#L65-L79)) — không gọi LLM, không gọi tool, in sẵn 2 bước:

> *"Tìm thấy 2 phòng trọ phù hợp: 1) Phòng Dịch Vọng (3.5tr/tháng), 2) Studio Quan Hoa (3.8tr/tháng)"*

**Hai căn này không tồn tại trong `data/properties.json`.** Đây là dữ liệu bịa nằm trong code.

CLAUDE.md mục 7 gọi đây là *"Agent trở thành chatbot đóng vai, không phải agent thật"* — ở đây còn nặng hơn: **Observation do lập trình viên viết sẵn**, không phải do tool sinh ra.

**Còn thiếu:**

1. 🔴 **Vòng lặp ReAct thật**: `gọi LLM ➔ parse "Action: tên[tham số]" ➔ tra AVAILABLE_TOOLS ➔ chạy tool ➔ nhét kết quả vào prompt làm Observation ➔ lặp`
2. 🔴 **Observation phải do code Python chèn** — LLM tự sinh chữ `Observation:` thì cắt bỏ
3. 🟡 **Khôi phục `run_all_test_cases()`** đã revert ở `4b1b15e`
4. 🟡 Bỏ / cho phép bỏ qua `input()` ([app.py:103](../src/app.py#L103)) — đang chặn chạy tự động
5. ℹ️ Nhớ `json.dumps(..., ensure_ascii=False)` vì tool trả `dict`/`list`

---

### ⏳ Role 5 — Hùng (tôi) · `docs/trace_eval.md`

| Mốc | Yêu cầu | Trạng thái |
| :-: | :--- | :-- |
| 1 | Scoring Matrix | ✅ 18/20 |
| 2 | Ghi phản hồi Chatbot gốc | ✅ 5/5 case log thật, rubric Chatbot `20/40` |
| 3 | Trích `Thought ➔ Action ➔ Observation` | ⏳ **chờ Role 4** |

**Không có cách lách.** Chuỗi đó chỉ tồn tại khi loop chạy thật.

**Chuẩn bị được trước:** dựng khung trace 5 case · bảng kiểm G1–G6 · điền 4/5 ô RCA *(mục 5 đang trống, Mốc 4 bắt buộc phải có ≥1 failed trace thật)*.

---

## 5. 🎯 ĐƯỜNG GĂNG — LÀM GÌ TRƯỚC

```
Role 3 merge ──┐
               ├──➔ Role 4 lắp ReAct loop ──➔ Role 5 trích trace ──➔ Mốc 3 XONG
Role 2 sửa  ───┘                          └──➔ Role 1 kiểm bẫy tầng agent
```

| Ưu tiên | Ai | Việc | Vì sao gấp |
| :-: | :--- | :--- | :--- |
| **1** | Role 3 | Merge `25a32ba` vào `main` | Việc **đã xong**, chỉ chờ merge. Rẻ nhất, gỡ ngay 2 blocker |
| **2** | **Role 4** | Viết vòng lặp ReAct thật | 🔴 **Chặn cả nhóm.** Không có cái này, Mốc 3 trượt |
| **3** | Role 2 | Thêm ghi file + kiểm `status` cho `create_booking` | Quyết định bằng chứng `6 ➔ 7` có tồn tại không |
| **4** | Role 1 | Sửa tên tool trong `test_cases.json` | 2 phút, không chờ ai |
| **5** | Role 5 | Dựng khung trace + RCA | Làm trước, chờ số liệu điền vào |

> 💡 **Việc gấp nhất của tôi lúc này không phải viết tài liệu, mà là hối Role 4.** Role 3 xong rồi, Role 2 sửa được trong 15 phút. Chỉ còn Role 4 là mắt xích thật sự.

---

## 6. 📌 CHƯA AI NHẬN — `docs/hybrid_flowchart.mermaid`

File này **chưa tồn tại**. Theo phân công là **Role 5B**, nhưng nhóm 5 người nên không có 5B ➔ mặc định rơi vào **Role 5 = tôi**.

Là việc của **Mốc 4**, chưa gấp. Nhưng nội dung thì tôi đã có sẵn từ Mốc 2 — dữ liệu thật để vẽ phân luồng:

* **Case 1** (cọc mấy tháng, giấy tờ gì) ➔ Chatbot **thắng**, đạt `8/8` rubric. Agent gọi tool ở đây là lãng phí
* **Case 2–5** ➔ Chatbot chỉ được `3/8`, bắt buộc đi nhánh Agent

---

## 7. ✅ TÓM TẮT MỘT CÂU MỖI NGƯỜI

| Role | Một câu |
| :--- | :--- |
| **1 — Hùng** | Xong, chỉ cần sửa 3 chỗ tên tool cho khớp Role 2 |
| **2 — Quan** | Tool chắc chắn, không crash — nhưng `create_booking` **không ghi file** và **không kiểm status** |
| **3 — Thắng** | Làm tốt nhất nhóm, **đã xong Mốc 3**, chỉ cần **merge** |
| **4 — Tín** | 🔴 ReAct loop vẫn hardcode — **đây là điểm nghẽn duy nhất của cả nhóm** |
| **5 — Hùng** | Xong Mốc 1+2, Mốc 3 chờ Role 4 |
