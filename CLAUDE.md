# CLAUDE.md — RentMate Agent

> Hướng dẫn cho AI (và cho thành viên nhóm) khi làm việc trong repo này.
> Đọc file này TRƯỚC khi sửa bất kỳ file nào.

---

## 1. Đề tài & bối cảnh

**RentMate — Trợ Lý Tìm & Đặt Lịch Xem Nhà Trọ / Căn Hộ Cho Thuê** (đề tài #10 trong `docs/DANH_SACH_DE_TAI.md`).

Người dùng là **sinh viên / người đi làm tại Hà Nội** đang tìm chỗ thuê. Họ hỏi kiểu:

> "Tìm cho tôi phòng trọ dưới 4 triệu gần Đại học Bách Khoa, rồi đặt lịch xem nhà chiều mai."

Bài toán này **cần Agent chứ không chỉ Chatbot**, vì:

| Tiêu chí Agentic Fit | Lý do đạt |
| :--- | :--- |
| Cần dữ liệu ngoài | Giá phòng, tình trạng còn/đã thuê nằm trong dữ liệu, LLM không tự biết |
| Nhiều bước phụ thuộc | Tìm căn ➔ lấy chi tiết ➔ xem lịch trống ➔ đặt lịch (bước sau cần output bước trước) |
| Có hành động thật | `book_viewing` **ghi dữ liệu** — không chỉ trả lời suông |
| Có rủi ro cần chặn | Đặt trùng lịch, đặt căn đã cho thuê, quận không tồn tại ➔ cần Guardrail |

Chatbot baseline sẽ **bịa** giá và số điện thoại chủ nhà. Đó chính là điểm so sánh của bài lab.

---

## 2. Kiến trúc

```
User (Web UI / CLI)
  │
  ├─► Chatbot Baseline ──► 1 LLM call ──► câu trả lời (0 tool, không grounded)
  │
  └─► ReAct Agent ──► vòng lặp Thought → Action → Observation
                            │
                            ├─► src/tools.py  (Tool Registry)
                            │        └─► data/*.json   ← "database" mock
                            └─► Observation ghép ngược vào prompt
                            (dừng khi Final Answer hoặc chạm MAX_ITERATIONS)
```

Điểm mấu chốt: **`data/*.json` là nguồn sự thật duy nhất.** Mọi con số trong câu trả lời cuối phải truy ngược được về một Observation, và Observation phải đọc từ file JSON.

---

## 3. Bản đồ file & chủ sở hữu (Zero-Conflict Workflow)

Mỗi role chỉ sửa file của mình để không conflict git.

| File | Role | Vai trò |
| :--- | :--- | :--- |
| `config/test_cases.json` | Role 1 — Product Architect | Bộ 5 test case |
| `src/tools.py` | Role 2 — Tool Engineer | Định nghĩa tool + đọc/ghi `data/` |
| `src/prompts.py` | Role 3 — Prompt Engineer | System prompt + `MAX_ITERATIONS` |
| `src/app.py` | Role 4 — Integrator | Vòng lặp ReAct, chạy CLI |
| `src/web.py` | Role 4 | Web FastAPI |
| `docs/trace_eval.md` | Role 5 — Observability | Trace log + Scoring Matrix |
| `docs/hybrid_flowchart.mermaid` | Role 5B | Sơ đồ phân luồng Chatbot vs Agent |
| `data/*.json` | Role 1 + Role 2 | Mock data (xem mục 5) |
| `src/providers.py` | — | **Không sửa.** Adapter đa nhà cung cấp LLM, đã chạy tốt |

---

## 4. Lệnh hay dùng

```bash
# Cài môi trường (chạy 1 lần)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env               # rồi điền API key

# Chạy bản CLI (demo Chatbot vs Agent trên 5 test case)
python src/app.py

# Chạy web FastAPI
uvicorn src.web:app --reload --port 8000
# ➔ mở http://127.0.0.1:8000

# Test riêng tool, không cần LLM (làm trước khi gắn Agent)
python src/tools.py

# Kiểm tra adapter LLM
python src/providers.py
```

Đổi nhà cung cấp LLM: sửa `LLM_PROVIDER` trong `.env` (`gemini` | `openai` | `anthropic` | `openrouter` | `mock`).
**`mock` chạy offline không cần API key** — dùng khi mạng lab chập chờn hoặc hết quota.

---

## 5. Mock data — schema `data/`

Không dùng database thật. Dữ liệu là 5 file JSON, thiết kế như DB quan hệ thu nhỏ (có khóa ngoại thật) để Agent buộc phải gọi nhiều tool nối tiếp nhau.

| File | Vai trò | Khóa |
| :--- | :--- | :--- |
| `data/landlords.json` | Chủ nhà / môi giới | `id` = `LL01`… |
| `data/properties.json` | **Bảng chính** — các căn cho thuê | `id` = `P001`…, `landlord_id` → landlords |
| `data/viewing_slots.json` | Khung giờ trống xem nhà | `property_id` → properties |
| `data/bookings.json` | Lịch hẹn đã đặt — **file duy nhất bị GHI** | `booking_id` = `BK...` |
| `data/districts.json` | Danh mục quận hợp lệ ở Hà Nội | dùng để validate input |

### Cấu trúc một căn hộ (`properties.json`)

```jsonc
{
  "id": "P001",
  "title": "...",
  "landlord_id": "LL01",          // khóa ngoại
  "type": "phòng trọ",            // phòng trọ | chung cư mini | studio | căn hộ dịch vụ | nhà nguyên căn
  "address": { "street", "ward", "district", "city" },
  "price_vnd": 3200000,           // giá thuê / tháng
  "deposit_months": 1,
  "area_m2": 20, "bedrooms": 1, "bathrooms": 1, "floor": 3, "has_elevator": false,
  "furnishing": "cơ bản",         // đầy đủ | cơ bản | trống
  "amenities": ["wifi", "điều hòa", ...],
  "utilities": { "electricity_per_kwh", "water_per_m3", "service_fee_vnd", "parking_fee_vnd" },
  "rules": { "pets_allowed", "curfew", "max_occupants" },
  "available_from": "2026-08-01",
  "status": "available",          // available | pending | rented
  "near": [ { "landmark": "ĐH Quốc Gia HN", "distance_km": 0.8 } ]
}
```

### Quy ước dữ liệu — nhớ kỹ

- **Tiền luôn là số nguyên VNĐ**, không phải chuỗi `"3.2 triệu"`. Việc format cho đẹp là của tầng hiển thị.
- **Ngày luôn `YYYY-MM-DD`**, giờ luôn `HH:MM` 24h.
- `status` khác `available` ➔ tool **phải từ chối đặt lịch**, kèm lý do rõ ràng.
- Dữ liệu cố tình có "mìn" để test Agent, đừng "dọn dẹp" chúng đi:
  - `P009`, `P012` = `rented` và `P015` = `pending` ➔ test nhánh từ chối đặt lịch
  - `P013` còn trống nhưng **đã kín toàn bộ slot** ➔ test fallback khi không còn lịch
  - `districts.json` chỉ chứa quận có thật ➔ hỏi "quận Atlantis" phải ra lỗi
- `bookings.json` có sẵn **6 lịch mẫu** khớp với các slot `is_booked: true`. Hai file này phải luôn đồng bộ: `book_viewing` ghi thêm 1 booking thì đồng thời phải set `is_booked = true` cho slot tương ứng.
- Demo xong muốn reset dữ liệu về ban đầu: `git checkout data/`

---

## 6. Quy ước code bắt buộc

Đây là các tiêu chí bị chấm điểm. Vi phạm là mất điểm.

### Tool (`src/tools.py`)

1. **Tool KHÔNG BAO GIỜ raise exception.** Lỗi nghiệp vụ là *dữ liệu để Agent suy luận tiếp*, không phải sự cố làm sập app. Luôn `return "LỖI: <mô tả cụ thể + gợi ý cách sửa>"`.
   ```python
   # ĐÚNG
   return f"LỖI: Không tìm thấy quận '{district}'. Các quận hợp lệ: Cầu Giấy, Đống Đa, ..."
   # SAI
   raise ValueError("district not found")
   ```
2. **Tool trả về `str`**, đọc lên là hiểu ngay — vì chuỗi này bị nhét thẳng vào prompt làm Observation.
3. Mỗi tool có **docstring đủ 8 mục**: tên, mục đích, input schema, output schema, error semantics, side effect, ví dụ, an toàn.
4. Đăng ký tool vào dict `AVAILABLE_TOOLS` ở cuối file, nếu không Agent không gọi được.
5. **Chỉ `book_viewing` được ghi file.** Mọi tool khác là read-only.

### Vòng lặp ReAct (`src/app.py`)

1. **Luôn có phanh `MAX_ITERATIONS`.** Không có = lặp vô hạn = trượt tiêu chí Guardrails.
2. **Mỗi Action ➔ đúng 1 Observation, do code Python chèn vào.** Nếu LLM tự sinh chữ "Observation:", phải cắt bỏ — để nó tự bịa Observation là lỗi nặng nhất của bài lab.
3. Observation của bước N **phải xuất hiện trong prompt** của bước N+1.
4. Chạm `MAX_ITERATIONS` ➔ trả lời fallback lịch sự bằng tiếng Việt, không crash, không im lặng.
5. Gọi tool không tồn tại ➔ trả về danh sách tool hợp lệ để LLM tự sửa ở vòng sau.

### Chatbot baseline (`src/prompts.py`)

**Baseline phải "dốt" một cách trung thực** thì việc so sánh mới công bằng:
- Đúng **1 LLM call**, số lần gọi tool = **0**
- **Không** nhúng sẵn dữ liệu nhà/giá vào system prompt
- Không được khẳng định "đã đặt lịch xong cho bạn"

### Chung

- Mọi text hướng tới người dùng viết bằng **tiếng Việt có dấu**.
- Ghi log rõ `Thought:` / `Action:` / `Observation:` / `Final Answer:` — Role 5 copy thẳng vào `docs/trace_eval.md`.

---

## 7. Cạm bẫy thường gặp

| Cạm bẫy | Hậu quả |
| :--- | :--- |
| Commit file `.env` | Lộ API key. `.gitignore` đã chặn — đừng dùng `git add -f` |
| Đưa dữ liệu nhà vào system prompt của baseline | Baseline "gian lận", so sánh mất ý nghĩa, mất điểm mục 1 |
| Để LLM tự sinh Observation | Agent trở thành chatbot đóng vai, không phải agent thật |
| Quên `MAX_ITERATIONS` | Lặp vô hạn, đốt quota API |
| Sửa `data/*.json` bằng tay lúc đang demo | Agent và UI đọc lệch nhau, trace log sai |
| Hardcode đường dẫn `data/` | Chạy từ thư mục khác là gãy — luôn build path từ `__file__` |
| Ghi `bookings.json` mà không đọc lại trước | Mất lịch của lần đặt trước đó |

---

## 8. Trạng thái hiện tại

- [x] `src/providers.py` — adapter đa LLM, chạy được
- [x] `data/*.json` — mock data
- [ ] `src/tools.py` — **đang là tool thời tiết/vé máy bay của boilerplate, phải viết lại theo đề tài thuê nhà**
- [ ] `src/prompts.py` — prompt vẫn của đề tài cũ
- [ ] `src/app.py` — `run_react_agent()` đang **hardcode** step 1 / step 2, chưa gọi LLM thật. Phải viết lại hoàn toàn thành vòng lặp thực
- [ ] `config/test_cases.json` — vẫn là 5 câu thời tiết/vé máy bay
- [ ] `src/web.py` — chưa có
- [ ] `docs/trace_eval.md` — chưa có trace thật
