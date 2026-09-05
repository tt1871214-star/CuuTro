import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.entities import (
    Role,
    User,
    RescueTeam,
    Zone,
    ZoneThresholdConfig,
    AssemblyPoint,
    EmergencyContact,
    Alert,
    CommunityPost
)

def run_seed():
    print("Bắt đầu khởi tạo dữ liệu mẫu cho hệ thống CỨU TRỢ...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. ROLES
        roles_dict = {}
        for role_name in ["PEOPLE", "RESCUE_TEAM", "ADMIN"]:
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name)
                db.add(role)
                db.commit()
                db.refresh(role)
            roles_dict[role_name] = role
        print("✓ Đã khởi tạo 3 Roles: PEOPLE, RESCUE_TEAM, ADMIN")

        # 2. ZONE THRESHOLD CONFIG
        config = db.query(ZoneThresholdConfig).first()
        if not config:
            config = ZoneThresholdConfig(
                yellow_max=20,
                orange_max=50,
                red_min=50,
                description="Cấu hình ngưỡng số lượng yêu cầu cứu hộ phân mức Zone (Vàng: 0-19 | Cam: 20-49 | Đỏ: >= 50)"
            )
            db.add(config)
            db.commit()
            print("✓ Đã cấu hình ngưỡng Zone Engine: Vàng < 20, Cam 20-49, Đỏ >= 50")

        # 3. ZONES
        zones_data = [
            ("ZONE-HN-01", "Khu vực Hoàn Kiếm - Ba Đình", "Trung tâm thủ đô, đê bao sông Hồng", 21.0285, 105.8542, 6.0),
            ("ZONE-HN-02", "Khu vực Cầu Giấy - Nam Từ Liêm", "Vùng trũng thoát nước sông Nhuệ, nguy cơ ngập úng đô thị", 21.0360, 105.7830, 7.0),
            ("ZONE-HN-03", "Khu vực Hoàng Mai - Thanh Trì", "Khu vực ven sông Hồng, triều cường và ngập úng sâu", 20.9750, 105.8450, 8.0),
            ("ZONE-DN-01", "Khu vực Liên Chiểu - Hòa Vang (Đà Nẵng)", "Vùng sườn núi nguy cơ sạt lở đất và lũ quét", 16.0748, 108.1499, 10.0),
            ("ZONE-HUE-01", "Khu vực Hương Trà - Hương Thủy (Huế)", "Vùng hạ lưu sông Hương, ngập lụt diện rộng mùa mưa bão", 16.4637, 107.5909, 10.0)
        ]

        created_zones = []
        for code, name, desc, lat, lng, radius in zones_data:
            zone = db.query(Zone).filter(Zone.code == code).first()
            if not zone:
                zone = Zone(
                    code=code,
                    name=name,
                    description=desc,
                    center_lat=lat,
                    center_lng=lng,
                    radius_km=radius,
                    request_count=0,
                    status="YELLOW"
                )
                db.add(zone)
                db.commit()
                db.refresh(zone)
            created_zones.append(zone)
        print(f"✓ Đã khởi tạo {len(created_zones)} phân vùng Zone cứu trợ thực tế.")

        # 4. DEFAULT USERS
        # Admin
        admin = db.query(User).filter(User.phone == "0901234567").first()
        if not admin:
            admin = User(
                phone="0901234567",
                password_hash=get_password_hash("admin123"),
                full_name="Ban Chỉ Huy Ứng Phó Thiên Tai & Cứu Hộ",
                role_id=roles_dict["ADMIN"].id,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✓ Tạo tài khoản Quản trị viên: 0901234567 / admin123")

        # Rescue Team 1
        rescue_user = db.query(User).filter(User.phone == "0912345678").first()
        if not rescue_user:
            rescue_user = User(
                phone="0912345678",
                password_hash=get_password_hash("rescue123"),
                full_name="Đội Cứu Nạn Khẩn Cấp Hà Nội",
                role_id=roles_dict["RESCUE_TEAM"].id,
                is_active=True
            )
            db.add(rescue_user)
            db.commit()
            db.refresh(rescue_user)

            team = RescueTeam(
                user_id=rescue_user.id,
                team_name="Đội Xuồng Cứu Nạn Chuyên Nghiệp 114",
                leader_name="Đại úy Nguyễn Văn Hùng",
                contact_phone="0912345678",
                status="ACTIVE",
                current_lat=21.0285,
                current_lng=105.8542,
                assigned_zone_id=created_zones[0].id
            )
            db.add(team)
            db.commit()
            print("✓ Tạo tài khoản Đội cứu hộ 1: 0912345678 / rescue123")

        # Rescue Team 2
        rescue_user2 = db.query(User).filter(User.phone == "0934567890").first()
        if not rescue_user2:
            rescue_user2 = User(
                phone="0934567890",
                password_hash=get_password_hash("rescue123"),
                full_name="Đội Phản Ứng Nhanh Chữ Thập Đỏ",
                role_id=roles_dict["RESCUE_TEAM"].id,
                is_active=True
            )
            db.add(rescue_user2)
            db.commit()
            db.refresh(rescue_user2)

            team2 = RescueTeam(
                user_id=rescue_user2.id,
                team_name="Biệt Đội Ca Nô & Cứu Hộ Đô Thị Cầu Giấy",
                leader_name="Lê Hoàng Nam",
                contact_phone="0934567890",
                status="ACTIVE",
                current_lat=21.0360,
                current_lng=105.7830,
                assigned_zone_id=created_zones[1].id
            )
            db.add(team2)
            db.commit()
            print("✓ Tạo tài khoản Đội cứu hộ 2: 0934567890 / rescue123")

        # Citizen
        citizen = db.query(User).filter(User.phone == "0987654321").first()
        if not citizen:
            citizen = User(
                phone="0987654321",
                password_hash=get_password_hash("citizen123"),
                full_name="Trần Thị Mai (Cư dân)",
                role_id=roles_dict["PEOPLE"].id,
                is_active=True
            )
            db.add(citizen)
            db.commit()
            print("✓ Tạo tài khoản Người dân: 0987654321 / citizen123")

        # 5. ASSEMBLY POINTS & REFUGES
        places = [
            ("Cung Điền Kinh Trong Nhà Hà Nội", "REFUGE", "Đường Trần Hữu Dực, Phường Cầu Diễn, Nam Từ Liêm", 21.0305, 105.7685, 2500, "Đ/c Trần Trọng Hải", "02438541234"),
            ("Nhà Thi Đấu Cầu Giấy", "ASSEMBLY", "Số 35 Trần Quý Kiên, Dịch Vọng, Cầu Giấy", 21.0358, 105.7925, 1200, "Đ/c Lê Văn Quân", "02437549876"),
            ("Trường THPT Chu Văn An", "ASSEMBLY", "Số 10 Thụy Khuê, Tây Hồ, Hà Nội", 21.0435, 105.8340, 800, "Cô Vũ Thị Lan", "02438234567"),
            ("Trung Tâm Văn Hóa Thể Thao Hoàng Mai", "REFUGE", "Đường Linh Đường, Hoàng Liệt, Hoàng Mai", 20.9680, 105.8360, 1800, "Đ/c Hoàng Anh Tuấn", "02436421234")
        ]
        for name, p_type, addr, lat, lng, cap, contact, phone in places:
            existing = db.query(AssemblyPoint).filter(AssemblyPoint.name == name).first()
            if not existing:
                ap = AssemblyPoint(
                    name=name,
                    point_type=p_type,
                    address=addr,
                    latitude=lat,
                    longitude=lng,
                    capacity=cap,
                    current_occupancy=0,
                    contact_person=contact,
                    contact_phone=phone,
                    is_open=True
                )
                db.add(ap)
        db.commit()
        print("✓ Đã khởi tạo các Điểm tập kết (Assembly) và Nơi trú ẩn (Refuge).")

        # 6. EMERGENCY CONTACTS
        hotlines = [
            ("Tìm kiếm cứu nạn toàn quốc", "112", "Cứu hộ khẩn cấp tai nạn, sự cố, thiên tai trên toàn lãnh thổ", "shield-alert", 1),
            ("Cảnh sát PCCC & Cứu nạn cứu hộ", "114", "Ứng cứu hỏa hoạn, đuối nước, sập đổ công trình, mắc kẹt lũ lụt", "flame", 2),
            ("Cấp cứu Y tế khẩn cấp", "115", "Hỗ trợ sơ cấp cứu và chuyển tuyến nạn nhân chấn thương nặng", "ambulance", 3),
            ("Cảnh sát phản ứng nhanh", "113", "Bảo đảm an ninh trật tự, điều phối giao thông vùng thiên tai", "shield", 4),
            ("Đường dây nóng PCTT Quốc Gia", "18001091", "Ban chỉ đạo Quốc gia về Phòng chống thiên tai", "phone-call", 5)
        ]
        for name, phone, desc, icon, order in hotlines:
            existing = db.query(EmergencyContact).filter(EmergencyContact.phone == phone).first()
            if not existing:
                c = EmergencyContact(
                    name=name,
                    phone=phone,
                    description=desc,
                    icon_type=icon,
                    sort_order=order,
                    is_active=True
                )
                db.add(c)
        db.commit()
        print("✓ Đã khởi tạo Danh bạ cứu nạn khẩn cấp quốc gia (112, 114, 115...).")

        # 7. COMMUNITY INITIAL REPORTS
        initial_posts = [
            ("Đoạn đường Trần Duy Hưng ngập sâu 60cm, nhiều xe máy chết máy", "Khu vực trước Big C Thăng Long nước ngập lút bánh xe, các phương tiện ô tô con và xe máy không nên di chuyển qua đây.", "FLOOD", 21.0080, 105.7950, "VERIFIED", 5, 0),
            ("Cây xà cừ cổ thụ bật gốc chắn ngang đường Hoàng Hoa Thám", "Cây đổ đè đứt dây điện, đã có lực lượng chức năng phong tỏa, khuyến cáo đi đường Thụy Khuê thay thế.", "ROAD_DAMAGE", 21.0390, 105.8200, "VERIFIED", 4, 0),
            ("Mất điện toàn bộ khu vực ngõ 165 Cầu Giấy do chập trạm biến áp", "Nước dâng sát trạm điện nên điện lực đã chủ động cắt điện an toàn, bà con cần tích trữ nước sinh hoạt.", "POWER_OUTAGE", 21.0330, 105.7980, "UNVERIFIED", 1, 0)
        ]
        for title, content, p_type, lat, lng, v_status, c_count, d_count in initial_posts:
            existing = db.query(CommunityPost).filter(CommunityPost.title == title).first()
            if not existing and citizen:
                post = CommunityPost(
                    user_id=citizen.id,
                    title=title,
                    content=content,
                    post_type=p_type,
                    latitude=lat,
                    longitude=lng,
                    verification_status=v_status,
                    confirm_count=c_count,
                    deny_count=d_count
                )
                db.add(post)
        db.commit()
        print("✓ Đã nạp tin tức thực địa mẫu trên Bảng tin cộng đồng.")

        print("\n🎉 KHỞI TẠO DỮ LIỆU SEED THÀNH CÔNG RỰC RỠ!")
    except Exception as e:
        db.rollback()
        print("❌ Lỗi khi seed dữ liệu:", e)
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
