"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_json(filename):
    """
    Đọc một file JSON trong thư mục data và trả về dữ liệu Python.

    Args:
        filename (str): Tên file JSON.

    Returns:
        dict | list: Dữ liệu sau khi parse JSON.
    """
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)
PROPERTIES = load_json("properties.json")
DISTRICTS = load_json("districts.json")
LANDLORDS = load_json("landlords.json")
BOOKINGS = load_json("bookings.json")
VIEWING_SLOTS = load_json("viewing_slots.json")

def validate_district(district: str) -> str:
    """
    Kiểm tra xem quận người dùng nhập có nằm trong danh sách hỗ trợ hay không.

    Args:
        district (str):
            Tên quận người dùng nhập.
            Ví dụ:
                - "Cầu Giấy"
                - "Đống Đa"
                - "Nam Từ Liêm"

    Returns:
        str:
            - "VALID" nếu quận hợp lệ.
            - Chuỗi lỗi nếu quận không tồn tại.
    """

    keyword = district.lower().strip()

    for item in DISTRICTS["districts"]:

        if keyword == item["name"].lower():
            return "VALID"

        if keyword in item["aliases"]:
            return "VALID"

    return f"LỖI: Quận '{district}' không tồn tại trong hệ thống."

def search_properties(
    district: str,
    max_price: int = None,
    property_type: str = None
) -> list:
    """
    Tìm kiếm phòng trọ/căn hộ theo điều kiện.

    Args:
        district (str):
            Quận cần tìm.

        max_price (int, optional):
            Giá thuê tối đa (VNĐ).

        property_type (str, optional):
            Loại bất động sản.
            Ví dụ:
                - phòng trọ
                - chung cư mini
                - studio
                - căn hộ dịch vụ

    Returns:
        list:
            Danh sách các bất động sản phù hợp.
            Nếu không có sẽ trả về danh sách rỗng.
    """

    # Kiểm tra quận
    if validate_district(district) != "VALID":
        return []

    results = []

    for property in PROPERTIES:

        # Chỉ lấy nhà còn trống
        if property["status"] != "available":
            continue

        # Lọc theo quận
        if property["address"]["district"].lower() != district.lower():
            continue

        # Lọc theo giá
        if max_price is not None:
            if property["price_vnd"] > max_price:
                continue

        # Lọc theo loại
        if property_type is not None:
            if property["type"].lower() != property_type.lower():
                continue

        results.append(property)

    return results

def get_property_details(property_id: str) -> dict:
    """
    Lấy toàn bộ thông tin chi tiết của một bất động sản.

    Args:
        property_id (str):
            Mã bất động sản.

    Returns:
        dict:
            Thông tin bất động sản.
            Nếu không tìm thấy trả về None.
    """

    for property in PROPERTIES:

        if property["id"] == property_id:
            return property

    return None

def get_available_slots(property_id: str) -> list:
    """
    Lấy các lịch xem nhà còn trống.

    Args:
        property_id (str):
            Mã bất động sản.

    Returns:
        list:
            Danh sách slot chưa được đặt.
    """

    available_slots = []

    for slot in VIEWING_SLOTS:

        if slot["property_id"] != property_id:
            continue

        if slot["is_booked"]:
            continue

        available_slots.append(slot)

    return available_slots

def get_booking(booking_id: str) -> dict:
    """
    Tra cứu thông tin một lịch hẹn.

    Args:
        booking_id (str):
            Mã booking.

    Returns:
        dict:
            Thông tin booking.
            Nếu không tìm thấy trả về None.
    """

    for booking in BOOKINGS:

        if booking["booking_id"] == booking_id:
            return booking

    return None

def get_landlord_info(property_id: str) -> dict:
    """
    Lấy thông tin chủ nhà của một bất động sản.

    Args:
        property_id (str):
            Mã bất động sản.

    Returns:
        dict:
            Thông tin chủ nhà.
            Nếu không tìm thấy trả về None.
    """

    property = get_property_details(property_id)

    if property is None:
        return None

    landlord_id = property["landlord_id"]

    for landlord in LANDLORDS:

        if landlord["id"] == landlord_id:
            return landlord

    return None

def recommend_properties(property_id: str) -> list:
    """
    Gợi ý các bất động sản tương tự.

    Tiêu chí:
        - Cùng quận
        - Cùng loại
        - Đang còn trống

    Args:
        property_id (str):
            Mã bất động sản.

    Returns:
        list:
            Danh sách bất động sản gợi ý.
    """

    current = get_property_details(property_id)

    if current is None:
        return []

    recommendations = []

    for property in PROPERTIES:

        if property["id"] == property_id:
            continue

        if property["status"] != "available":
            continue

        if property["address"]["district"] != current["address"]["district"]:
            continue

        if property["type"] != current["type"]:
            continue

        recommendations.append(property)

    return recommendations

from datetime import datetime


def create_booking(
    property_id: str,
    slot_id: str,
    customer_name: str,
    customer_phone: str,
    note: str = ""
) -> dict:
    """
    Tạo một lịch hẹn xem nhà.

    Args:
        property_id (str):
            Mã bất động sản.

        slot_id (str):
            Mã khung giờ xem.

        customer_name (str):
            Tên khách hàng.

        customer_phone (str):
            Số điện thoại khách.

        note (str):
            Ghi chú thêm.

    Returns:
        dict:
            Booking vừa tạo hoặc thông báo lỗi.
    """

    # 1. Kiểm tra căn hộ có tồn tại không
    property_info = get_property_details(property_id)

    if property_info is None:
        return {
            "success": False,
            "message": "Không tìm thấy bất động sản."
        }

    # 2. Kiểm tra slot
    slot = None

    for s in VIEWING_SLOTS:
        if s["slot_id"] == slot_id and s["property_id"] == property_id:
            slot = s
            break

    if slot is None:
        return {
            "success": False,
            "message": "Không tìm thấy khung giờ."
        }

    # 3. Slot đã được đặt chưa
    if slot["is_booked"]:
        return {
            "success": False,
            "message": "Khung giờ này đã có người đặt."
        }

    # 4. Sinh mã booking
    booking_id = f"BK{len(BOOKINGS)+1:05d}"

    # 5. Tạo booking mới
    booking = {
        "booking_id": booking_id,
        "property_id": property_id,
        "slot_id": slot_id,
        "date": slot["date"],
        "time": slot["time"],
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "note": note,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "confirmed"
    }

    # 6. Thêm vào danh sách booking
    BOOKINGS.append(booking)

    # 7. Cập nhật slot
    slot["is_booked"] = True

    return {
        "success": True,
        "message": "Đặt lịch thành công.",
        "booking": booking
    }

# Danh sách các tool được đăng ký để Agent sử dụng
AVAILABLE_TOOLS = {
    "validate_district": validate_district,
    "search_properties": search_properties,
    "get_property_details": get_property_details,
    "get_available_slots": get_available_slots,
    "create_booking": create_booking,
    "get_booking": get_booking,
    "get_landlord_info": get_landlord_info,
    "recommend_properties": recommend_properties,
}

