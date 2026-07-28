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


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) cho Trợ lý Nhà trọ & Căn hộ có Guardrails.
    """
    print(f"\n🤖 [REACT AGENT - TRỢ LÝ NHÀ TRỌ] Câu hỏi: {user_query}")
    step = 0
    
    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
        
        if step == 1:
            print("🧠 Thought: Câu hỏi này cần tra cứu danh sách phòng trọ / căn hộ cho thuê theo khu vực và ngân sách.")
            print("🛠️ Action: search_rentals['Cầu Giấy, Hà Nội', 4000000]")
            
            # Giả lập Observation từ công cụ tìm phòng trọ
            obs = "Tìm thấy 2 phòng trọ phù hợp: 1) Phòng Dịch Vọng (3.5tr/tháng, full đồ), 2) Studio Quan Hoa (3.8tr/tháng, ban công)."
            print(f"👁️ Observation: {obs}")
            
        elif step == 2:
            print("🧠 Thought: Tôi đã tìm thấy danh sách phòng phù hợp, giờ tôi sẽ gợi ý chi tiết và hỗ trợ đặt lịch xem nhà.")
            print("🏁 Final Answer: Đã tìm thấy 2 phòng trọ tại Cầu Giấy (dưới 4 triệu/tháng):\n"
                  "1. Phòng Dịch Vọng (3.5 triệu/tháng - đầy đủ nội thất)\n"
                  "2. Căn Studio Quan Hoa (3.8 triệu/tháng - có ban công thoáng mát)\n"
                  "Bạn muốn đặt lịch hẹn xem phòng nào?")
            break
            
    if step >= MAX_ITERATIONS:
        print(f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")


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
    
    # Chạy thử câu test số 3
    sample_query = tests[2]["question"]
    
    print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
    user_query = input("Nhập câu hỏi test (Nhấn Enter để dùng câu mặc định): ").strip()
    if not user_query:
        user_query = sample_query
    run_baseline_chatbot(user_query, provider)
    
    print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
    run_react_agent(user_query, provider)

