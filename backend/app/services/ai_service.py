from typing import Dict, Any

KNOWLEDGE_BASE = {
    "đuối nước": (
        "CẤP CỨU ĐUỐI NƯỚC:\n"
        "1. Đưa nạn nhân lên khỏi mặt nước an toàn, đặt nằm nghiêng an toàn nếu nôn trớ.\n"
        "2. Kiểm tra nhịp thở và đường thở. Nếu ngưng thở, tiến hành ép tim ngoài lồng ngực (CPR) 30 lần ép tim và 2 lần hà hơi thổi ngạt liên tục.\n"
        "3. Giữ ấm cơ thể, thay quần áo ướt và gọi ngay Cấp cứu 115!"
    ),
    "chảy máu": (
        "CẦM MÁU KHẨN CẤP:\n"
        "1. Đeo găng tay hoặc dùng vải sạch ấn trực tiếp vào vết thương trong 10-15 phút.\n"
        "2. Nâng cao chi bị thương nếu không có gãy xương.\n"
        "3. Dùng băng cuộn cố định băng ép. Chỉ dùng garo nếu máu phun thành tia (động mạch lớn) và ghi rõ giờ đặt garo."
    ),
    "gãy xương": (
        "XỬ TRÍ GÃY XƯƠNG:\n"
        "1. Tuyệt đối không nắn bóp, không cố kéo thẳng chi bị gãy.\n"
        "2. Cố định chi bằng nẹp gỗ, cành cây hoặc bìa carton qua 2 khớp (khớp trên và khớp dưới ổ gãy).\n"
        "3. Chườm lạnh giảm đau và chuyển ngay đến cơ sở y tế gần nhất."
    ),
    "ngập lụt": (
        "HƯỚNG DẪN KHI BỊ NGẬP LỤT:\n"
        "1. Ngắt ngay cầu dao điện tổng, khóa van bình gas gia đình.\n"
        "2. Di chuyển người già, trẻ nhỏ và tài sản thiết yếu lên tầng cao hoặc điểm tránh trú.\n"
        "3. Không đi bộ, bơi lội hoặc lái xe qua vùng nước ngập sâu hoặc dòng chảy xiết.\n"
        "4. Bật tín hiệu SOS trên ứng dụng CỨU TRỢ để đội phản ứng nhanh định vị bạn."
    ),
    "sạt lở": (
        "ỨNG PHÓ SẠT LỞ ĐẤT ĐÁ:\n"
        "1. Quan sát dấu hiệu: nứt đất, cây nghiêng, nước sông suối chuyển màu đục ngầu bất thường, tiếng nổ lớn từ sườn đồi.\n"
        "2. Nhanh chóng di tản vuông góc với hướng trôi trượt của đất đá, chạy lên vị trí cao kiên cố.\n"
        "3. Tuyệt đối không quay lại nhà để lấy tài sản."
    ),
    "điện giật": (
        "CẤP CỨU ĐIỆN GIẬT:\n"
        "1. Ngắt nguồn điện ngay lập tức (dập cầu dao). Nếu không ngắt được, dùng vật cách điện (gỗ khô, gậy tre khô) tách nạn nhân ra khỏi nguồn điện.\n"
        "2. Không chạm tay trần vào người nạn nhân khi chưa cắt điện.\n"
        "3. Kiểm tra nhịp thở và hô hấp nhân tạo nếu cần, gọi ngay 115."
    )
}

def ask_first_aid_ai(query: str) -> Dict[str, Any]:
    q_lower = query.lower()
    for keyword, advice in KNOWLEDGE_BASE.items():
        if keyword in q_lower:
            return {
                "matched": True,
                "response": advice,
                "status": "RESOLVED",
                "source": "Relief First-Aid AI Assistant"
            }
    
    # Generic emergency guidance
    return {
        "matched": False,
        "response": (
            "Trợ lý CỨU TRỢ: Trong tình huống khẩn cấp, bạn vui lòng:\n"
            "1. Nhấn nút [GỬI YÊU CẦU CỨU TRỢ (SOS)] ở trang chủ để hệ thống tự động truyền tọa độ GPS tới Đội cứu hộ gần nhất.\n"
            "2. Hoặc gọi trực tiếp đường dây nóng 112 (Tìm kiếm cứu nạn), 114 (Cứu hỏa), 115 (Cấp cứu y tế).\n"
            "3. Giữ bình tĩnh, tiết kiệm pin điện thoại và tìm nơi cao ráo kiên cố."
        ),
        "status": "RESOLVED",
        "source": "Relief Emergency Guidance"
    }
