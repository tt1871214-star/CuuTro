from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False) # PEOPLE, RESCUE_TEAM, ADMIN

    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    rescue_team = relationship("RescueTeam", back_populates="user", uselist=False)
    rescue_requests = relationship("RescueRequest", back_populates="user", foreign_keys="RescueRequest.user_id")
    community_posts = relationship("CommunityPost", back_populates="author")
    safe_statuses = relationship("SafeStatus", back_populates="user")

class RescueTeam(Base):
    __tablename__ = "rescue_teams"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    team_name = Column(String(100), nullable=False)
    leader_name = Column(String(100), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    status = Column(String(20), default="ACTIVE") # ACTIVE, BUSY, INACTIVE
    current_lat = Column(Float, nullable=False, default=21.0285)
    current_lng = Column(Float, nullable=False, default=105.8542)
    assigned_zone_id = Column(Integer, ForeignKey("zones.id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="rescue_team")
    zone = relationship("Zone", back_populates="rescue_teams")
    assigned_requests = relationship("RescueRequest", back_populates="assigned_team")

class Zone(Base):
    __tablename__ = "zones"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True) # e.g. ZONE-BA-DINH
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    radius_km = Column(Float, default=5.0)
    request_count = Column(Integer, default=0) # Updated by Zone Engine
    status = Column(String(20), default="YELLOW") # YELLOW, ORANGE, RED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rescue_teams = relationship("RescueTeam", back_populates="zone")
    rescue_requests = relationship("RescueRequest", back_populates="zone")

class ZoneThresholdConfig(Base):
    __tablename__ = "zone_threshold_configs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    yellow_max = Column(Integer, default=20, nullable=False)  # 0 to yellow_max - 1 => YELLOW
    orange_max = Column(Integer, default=50, nullable=False)  # yellow_max to orange_max - 1 => ORANGE
    red_min = Column(Integer, default=50, nullable=False)     # >= red_min => RED
    description = Column(String(255), default="Cấu hình ngưỡng số lượng yêu cầu cứu hộ phân mức Zone (Vàng / Cam / Đỏ)")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RescueRequest(Base):
    __tablename__ = "rescue_requests"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id", ondelete="SET NULL"), nullable=True)
    sender_name = Column(String(100), nullable=True)
    sender_phone = Column(String(20), nullable=True)
    relief_type = Column(String(50), default="CỨU NGƯỜI MẮC KẸT") # CỨU NGƯỜI MẮC KẸT, Y TẾ KHẨN CẤP, LƯƠNG THỰC - NƯỚC UỐNG, DI TẢN, KHÁC
    personal_urgency = Column(String(30), default="CAO") # BÌNH THƯỜNG, CAO, KHẨN CẤP, NGUY KỊCH
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(30), default="PENDING", index=True) # PENDING -> ACCEPTED -> IN_PROGRESS -> COMPLETED or CANCELLED
    assigned_team_id = Column(Integer, ForeignKey("rescue_teams.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="rescue_requests", foreign_keys=[user_id])
    zone = relationship("Zone", back_populates="rescue_requests")
    assigned_team = relationship("RescueTeam", back_populates="assigned_requests")
    histories = relationship("RescueHistory", back_populates="request", cascade="all, delete-orphan")

class RescueHistory(Base):
    __tablename__ = "rescue_histories"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("rescue_requests.id", ondelete="CASCADE"), nullable=False)
    from_status = Column(String(30), nullable=True)
    to_status = Column(String(30), nullable=False)
    action = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    performed_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("RescueRequest", back_populates="histories")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    disaster_type = Column(String(50), default="BÃO / MƯA LŨ") # BÃO, MƯA LŨ, SẠT LỞ, NGẬP LỤT, THỜI TIẾT CỰC ĐOAN
    target_area = Column(String(150), nullable=False)
    alert_level = Column(String(20), default="ORANGE") # YELLOW, ORANGE, RED
    message = Column(Text, nullable=False)
    guidelines = Column(Text, nullable=True) # Hướng dẫn & khuyến nghị an toàn
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    radius_km = Column(Float, default=15.0)
    source = Column(String(50), default="OPEN_METEO") # MANUAL, OPEN_METEO
    created_at = Column(DateTime, default=datetime.utcnow)

class AssemblyPoint(Base):
    __tablename__ = "assembly_points"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    point_type = Column(String(30), default="ASSEMBLY") # ASSEMBLY (Điểm tập kết), REFUGE (Nơi trú ẩn)
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer, default=100)
    current_occupancy = Column(Integer, default=0)
    contact_person = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    is_open = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CommunityPost(Base):
    __tablename__ = "community_posts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    post_type = Column(String(50), nullable=False) # FLOOD, LANDSLIDE, ROAD_DAMAGE, BRIDGE_DAMAGE, POWER_OUTAGE, REFUGE, TRAFFIC, NEED_HELP
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    image_url = Column(String(255), nullable=True)
    verification_status = Column(String(20), default="UNVERIFIED") # UNVERIFIED, VERIFIED, REJECTED
    confirm_count = Column(Integer, default=0)
    deny_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User", back_populates="community_posts")
    verifications = relationship("CommunityVerification", back_populates="post", cascade="all, delete-orphan")

class CommunityVerification(Base):
    __tablename__ = "community_verifications"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_confirm = Column(Boolean, nullable=False) # True = xác nhận đúng, False = báo tin sai
    distance_km = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("CommunityPost", back_populates="verifications")
    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='unique_post_user_verify'),)

class SafeStatus(Base):
    __tablename__ = "safe_statuses"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status_message = Column(String(255), default="Tôi an toàn")
    battery_level = Column(Integer, nullable=True) # e.g. 85%
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="safe_statuses")

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    description = Column(String(200), nullable=True)
    icon_type = Column(String(50), default="phone")
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
