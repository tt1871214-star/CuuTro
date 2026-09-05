import time
from datetime import datetime
from database.db import db
from models.logs import AILog
from models.disaster import Disaster
from models.community import CommunityPost

# First Aid FAQs & Disaster Response Guidelines
FIRST_AID_FAQS = [
    {
        "keywords": ["sơ cứu", "đuối nước", "chết đuối", "ngạt nước"],
        "answer": "Sơ cứu đuối nước:\n1. Đưa nạn nhân lên bờ ngay lập tức.\n2. Đặt nạn nhân nằm ngửa trên nền cứng.\n3. Kiểm tra nhịp thở: Nếu ngừng thở, thực hiện ép tim ngoài lồng ngực (30 lần) kết hợp hà hơi thổi ngạt (2 lần).\n4. Liên hệ ngay cấp cứu 115 hoặc đội cứu hộ."
    },
    {
        "keywords": ["sạt lở", "đất đá", "núi lở"],
        "answer": "Kỹ năng sống sót khi sạt lở đất:\n1. Di tản ngay lập tức khỏi vùng cảnh báo nguy hiểm.\n2. Nếu không kịp di tản, cuộn tròn người như một quả bóng, bảo vệ đầu và gáy.\n3. Tìm kiếm vị trí trú ẩn vững chắc dưới gầm bàn, gầm giường vững chắc hoặc góc tường trong nhà."
    },
    {
        "keywords": ["lũ lụt", "ngập nước", "nước dâng"],
        "answer": "Ứng phó khi lũ lụt xảy ra:\n1. Ngắt ngay toàn bộ cầu dao điện trong nhà để tránh rò rỉ điện.\n2. Di chuyển các tài sản và bản thân lên các tầng cao hơn.\n3. Chuẩn bị phao tự chế, nước uống đóng chai và thực phẩm khô.\n4. Tuyệt đối không đi bộ hoặc lái xe qua vùng nước ngập chảy xiết."
    },
    {
        "keywords": ["sơ cứu", "chấn thương", "chảy máu", "băng bó"],
        "answer": "Sơ cứu chảy máu/chấn thương:\n1. Rửa sạch vết thương bằng nước sạch hoặc dung dịch sát khuẩn.\n2. Dùng gạc sạch ép trực tiếp lên vết thương để cầm máu.\n3. Băng bó cố định vết thương bằng băng thun hoặc vải sạch.\n4. Nếu nghi ngờ gãy xương, giữ nguyên tư thế và nẹp cố định trước khi di chuyển."
    },
    {
        "keywords": ["điểm cứu trợ", "nhận quà", "nhận cơm", "phát gạo"],
        "answer": "Để tìm các điểm cứu trợ, bạn có thể tra cứu trực tiếp trên Bản đồ cứu trợ (mục Điểm cứu trợ). Các điểm cứu trợ đã được cộng đồng xác thực sẽ hiển thị với màu sắc tương ứng. Hiện tại bạn có thể cập nhật thông tin qua bản đồ chính thức."
    }
]

class AIService:
    def query(self, user_id, query_text):
        """
        Handle resident queries regarding safety, first-aid, or disaster updates.
        Strictly use verified local data, FAQ rules, and log transactions.
        Must execute and respond in < 3 seconds.
        """
        start_time = time.time()
        query_lower = query_text.lower().strip()
        response = None
        status = 'RESOLVED'

        # 1. Search FAQ Local Guidelines
        for faq in FIRST_AID_FAQS:
            if any(kw in query_lower for kw in faq["keywords"]):
                response = faq["answer"]
                break

        # 2. Search Active Disasters if FAQ didn't match
        if not response:
            active_disasters = Disaster.query.filter_by(status='ACTIVE').all()
            disaster_matches = []
            for d in active_disasters:
                # Basic keyword matching on title/description
                if any(kw in query_lower for kw in d.title.lower().split() + d.description.lower().split()):
                    disaster_matches.append(f"- Cảnh báo {d.title}: {d.description} (Mức độ: {d.alert_level})")
            
            if disaster_matches:
                response = "Thông tin thiên tai đang hoạt động khớp với tìm kiếm của bạn:\n" + "\n".join(disaster_matches)

        # 3. Search Verified Community Posts
        if not response:
            verified_posts = CommunityPost.query.filter_by(verification_status='VERIFIED').all()
            post_matches = []
            for p in verified_posts:
                if any(kw in query_lower for kw in p.title.lower().split() + p.content.lower().split()):
                    post_type_vietnamese = {
                        'FLOOD': 'Ngập lụt',
                        'LANDSLIDE': 'Sạt lở',
                        'ROAD_DAMAGE': 'Đường hỏng',
                        'BRIDGE_DAMAGE': 'Cầu hỏng',
                        'RELIEF_POINT': 'Điểm cứu trợ',
                        'DANGER_ZONE': 'Khu vực nguy hiểm'
                    }.get(p.post_type, p.post_type)
                    post_matches.append(f"- [{post_type_vietnamese}] {p.title}: {p.content} (Tại tọa độ: {p.latitude}, {p.longitude})")
            
            if post_matches:
                response = "Thông báo xác thực từ cộng đồng liên quan:\n" + "\n".join(post_matches[:3])

        # 4. Fallback Rule: Transfer to human dispatcher
        if not response:
            response = "Xin lỗi, tôi không tìm thấy thông tin này trong cơ sở dữ liệu đã xác thực. Yêu cầu của bạn đã được chuyển cho người trực tổng đài để xử lý trực tiếp."
            status = 'TRANSFERRED'

        # Calculate time taken in milliseconds
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Log AI interaction to Database
        log = AILog(
            user_id=user_id,
            query=query_text,
            response=response,
            execution_time_ms=execution_time_ms,
            status=status,
            created_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

        return {
            'response': response,
            'status': status,
            'execution_time_ms': execution_time_ms
        }
