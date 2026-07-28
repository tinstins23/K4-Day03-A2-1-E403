"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
Đề tài: Trợ Lý Tìm & Đặt Lịch Xem Nhà Trọ / Căn Hộ Cho Thuê
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import sys
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")
    
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")


import ast
import re

def ep_kieu_tham_so(raw: str):
    """Chuyển một tham số dạng chuỗi của LLM về đúng kiểu Python.

    ⚠️ KHÔNG ép về int nếu chuỗi số bắt đầu bằng '0' — số điện thoại Việt Nam
    (0912345678) toàn chữ số, ép int sẽ nuốt mất số 0 đầu và lưu sai số của khách.
    Chỉ ép int cho số thật sự dùng để tính toán, ví dụ max_price = 4000000.
    """
    val = raw.strip().strip("'\"").strip()

    if val in ("None", "none", "null", ""):
        return None
    if val in ("True", "true"):
        return True
    if val in ("False", "false"):
        return False
    # "0912345678" ➔ giữ nguyên chuỗi · "4000000" ➔ int
    if val.isdigit() and not (len(val) > 1 and val.startswith("0")):
        return int(val)
    return val


def parse_action_string(text: str):
    """Trích xuất tên tool và danh sách tham số từ câu trả lời của LLM"""
    match = re.search(r"Action:\s*(\w+)\s*[\[\(](.*?)[\]\)]", text, re.DOTALL | re.IGNORECASE)
    if match:
        tool_name = match.group(1).strip()
        raw_args = match.group(2).strip()
        if not raw_args:
            return tool_name, []
        try:
            parsed = ast.literal_eval(f"[{raw_args}]")
            if isinstance(parsed, list):
                return tool_name, parsed
        except Exception:
            pass
        cleaned_args = [ep_kieu_tham_so(p) for p in raw_args.split(",")]
        return tool_name, cleaned_args

    match_colon = re.search(r"Action:\s*(\w+)\s*[:\s]\s*(.*)", text, re.IGNORECASE)
    if match_colon:
        tool_name = match_colon.group(1).strip()
        raw_args = match_colon.group(2).strip()
        cleaned_args = [ep_kieu_tham_so(p) for p in raw_args.split(",") if p.strip()]
        return tool_name, cleaned_args

    return None, []


def execute_tool_call(tool_name: str, args: list):
    """Gọi và thực thi công cụ từ AVAILABLE_TOOLS trong tools.py"""
    if tool_name not in AVAILABLE_TOOLS:
        return f"LỖI: Công cụ '{tool_name}' không tồn tại. Các công cụ khả dụng: {list(AVAILABLE_TOOLS.keys())}"

    func = AVAILABLE_TOOLS[tool_name]
    try:
        res = func(*args)
        if isinstance(res, (dict, list)):
            return json.dumps(res, ensure_ascii=False, indent=2)
        return str(res)
    except Exception as e:
        return f"LỖI thực thi tool '{tool_name}': {str(e)}"


def start_interactive_chat_session(provider, initial_query: str = ""):
    """
    Khởi chạy phiên trò chuyện tương tác đa lượt (Multi-turn Chat) với ReAct Agent.
    Duy trì bộ nhớ cuộc thoại (Context) liên tục và KHÔNG tự ngắt khi AI trả lời xong.
    """
    print("\n==================================================")
    print("💬 PHIÊN TRÒ CHUYỆN TƯƠNG TÁC ĐA LƯỢT VỚI REACT AGENT")
    print("👉 Gõ 'exit', 'quit' hoặc 'q' để thoát khỏi ứng dụng.")
    print("==================================================\n")
    
    conversation_history = ""
    first_turn = True
    
    while True:
        if first_turn and initial_query:
            user_input = initial_query
            first_turn = False
            print(f"👤 Người dùng: {user_input}")
        else:
            try:
                user_input = input("\n👤 Người dùng: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Đã kết thúc phiên trò chuyện.")
                break
                
        if not user_input:
            continue
            
        if user_input.lower() in ["exit", "quit", "q"]:
            print("👋 Cảm ơn bạn đã sử dụng Trợ lý Tìm & Đặt Lịch Xem Nhà Trọ!")
            break
            
        conversation_history = chay_mot_luot_react(user_input, provider, conversation_history)


def chay_mot_luot_react(user_input: str, provider, conversation_history: str = "") -> str:
    """Chạy trọn vòng lặp ReAct cho MỘT câu hỏi. Trả về lịch sử hội thoại đã cập nhật.

    Tách riêng khỏi phần `input()` để vừa dùng cho chế độ chat tương tác,
    vừa dùng cho chế độ chạy tự động toàn bộ test case (không cần người gõ).
    """
    conversation_history += f"Question: {user_input}\n"
    step = 0
    da_tra_loi = False

    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
        
        # 1. Gọi Model LLM thực tế để suy luận (Thought & Action)
        llm_output = provider.generate(conversation_history, system_prompt=REACT_SYSTEM_PROMPT).strip()

        # 🛡️ GUARDRAIL QUAN TRỌNG NHẤT: cắt bỏ Observation do LLM tự bịa.
        # Observation CHỈ được sinh ra từ kết quả tool thật (do code Python chèn
        # ở bước 3). Nếu để LLM tự viết Observation, nó sẽ tự đóng vai cả hệ
        # thống và bịa số liệu — Agent lúc đó chỉ là chatbot diễn kịch.
        if re.search(r"^\s*Observation\s*:", llm_output, re.IGNORECASE | re.MULTILINE):
            llm_output = re.split(
                r"^\s*Observation\s*:", llm_output, maxsplit=1,
                flags=re.IGNORECASE | re.MULTILINE
            )[0].strip()
            print("✂️  [ĐÃ CẮT] LLM tự bịa Observation — bỏ đi, chỉ dùng kết quả tool thật.")

            # Nếu cắt xong không còn gì, nghĩa là LLM CHỈ bịa Observation mà không
            # sinh Thought/Action nào. Không được coi đây là "model im lặng" rồi
            # thoát — phải nhắc lại định dạng và chạy tiếp, nếu không Agent sẽ
            # chết giữa chừng ở đúng những case nhiều bước (như case 3).
            if not llm_output:
                print("↩️  Nhắc lại định dạng cho LLM và chạy tiếp vòng sau.")
                conversation_history += (
                    "\nLƯU Ý HỆ THỐNG: Bạn KHÔNG được tự viết dòng 'Observation:'. "
                    "Observation chỉ do hệ thống cung cấp sau khi chạy tool thật. "
                    "Hãy trả lời lại theo đúng định dạng 'Thought: ...' rồi "
                    "'Action: tên_tool[tham_số]', hoặc 'Final Answer: ...' nếu đã đủ dữ liệu.\n"
                )
                continue

        print(f"🤖 LLM suy luận:\n{llm_output}")

        # Lưu phản hồi của LLM vào lịch sử cuộc thoại
        conversation_history += f"\n{llm_output}\n"
        
        # 2. Kiểm tra nếu LLM đưa ra kết quả cuối cùng (Final Answer)
        if "Final Answer:" in llm_output:
            final_answer = llm_output.split("Final Answer:", 1)[1].strip()
            print(f"\n🏁 [TRỢ LÝ TRẢ LỜI]:\n{final_answer}")
            da_tra_loi = True
            break
            
        # 3. Trích xuất Action và gọi Tool
        tool_name, args = parse_action_string(llm_output)
        if tool_name:
            print(f"🛠️ [THỰC THI TOOL]: {tool_name}{args}")
            obs = execute_tool_call(tool_name, args)
            print(f"👁️ [OBSERVATION (KẾT QUẢ TOOL)]:\n{obs}")
            
            # Cập nhật Observation vào lịch sử cuộc thoại
            conversation_history += f"Observation: {obs}\n"
        else:
            if not llm_output:
                print("⚠️ Model không trả về kết quả.")
                break
            print("ℹ️ Model dừng gọi tool, sẵn sàng nhận câu hỏi tiếp theo.")
            break

    # Chỉ báo chạm phanh khi THẬT SỰ hết vòng mà chưa có Final Answer
    if step >= MAX_ITERATIONS and not da_tra_loi:
        print(f"\n🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước suy luận.")
        print("🏁 [TRỢ LÝ TRẢ LỜI]:\nXin lỗi, yêu cầu của bạn cần nhiều bước tra cứu hơn "
              "mức cho phép nên tôi phải dừng lại để đảm bảo an toàn. "
              "Bạn vui lòng tách nhỏ câu hỏi giúp tôi nhé!")

    return conversation_history


def run_all_test_cases(provider):
    """Chạy tự động TOÀN BỘ test case: Chatbot Baseline vs ReAct Agent.

    Mỗi case là một hội thoại độc lập (lịch sử rỗng) để không lẫn ngữ cảnh.
    Dùng cho Role 5 lấy trace và Role 1 kiểm Guardrail — không cần gõ tay.
    """
    tests = load_test_cases()
    print(f"\n{'='*70}")
    print(f"🧪 CHẠY TỰ ĐỘNG {len(tests)} TEST CASES (Chatbot vs Agent)")
    print(f"{'='*70}")

    for tc in tests:
        print(f"\n\n{'#'*70}")
        print(f"# TEST CASE {tc['id']} — {tc.get('category','')}")
        print(f"# ❓ {tc['question']}")
        if tc.get("expected_tools"):
            print(f"# 🎯 Tool kỳ vọng: {', '.join(tc['expected_tools'])}")
        print(f"{'#'*70}")

        print("\n--- 🤖 CHATBOT BASELINE (0 tool) ---")
        run_baseline_chatbot(tc["question"], provider)

        print("\n--- 🧠 REACT AGENT ---")
        chay_mot_luot_react(tc["question"], provider, conversation_history="")

    print(f"\n{'='*70}")
    print("✅ ĐÃ CHẠY XONG TOÀN BỘ TEST CASES")
    print(f"{'='*70}")


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("🏠 ĐỀ TÀI: TRỢ LÝ TÌM & ĐẶT LỊCH XEM NHÀ TRỌ / CĂN HỘ CHO THUÊ")
    print("==================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    # Chế độ chạy tự động toàn bộ test case:  python src/app.py --all
    if "--all" in sys.argv:
        run_all_test_cases(provider)
        sys.exit(0)

    print("Chọn chế độ chạy:")
    print("  1. Chạy 1 câu hỏi (tự nhập hoặc dùng câu mặc định)")
    print("  2. Chạy tự động TOÀN BỘ test case  [hoặc: python src/app.py --all]")
    choice = input("Nhập lựa chọn (1 hoặc 2, mặc định 1): ").strip()

    if choice == "2":
        run_all_test_cases(provider)
    else:
        sample_query = tests[2]["question"]
        user_query = input("Nhập câu hỏi test (Nhấn Enter để dùng câu mặc định): ").strip()
        if not user_query:
            user_query = sample_query

        print("\n--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE (KHÔNG CÓ TOOL) ---")
        run_baseline_chatbot(user_query, provider)

        print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT (TƯƠNG TÁC ĐA LƯỢT LIÊN TỤC) ---")
        start_interactive_chat_session(provider, initial_query=user_query)



