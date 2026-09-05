import math
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.entities import Zone, ZoneThresholdConfig, RescueRequest

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers between two GPS coordinates."""
    R = 6371.0 # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_or_create_threshold_config(db: Session) -> ZoneThresholdConfig:
    """Retrieve existing threshold config or initialize default values."""
    config = db.query(ZoneThresholdConfig).first()
    if not config:
        config = ZoneThresholdConfig(
            yellow_max=20,
            orange_max=50,
            red_min=50,
            description="Cấu hình ngưỡng số lượng yêu cầu cứu hộ phân mức Zone (Vàng / Cam / Đỏ)"
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

def find_zone_for_coordinates(db: Session, lat: float, lng: float) -> Optional[Zone]:
    """Find the best matching Zone for given coordinates (within radius, or closest zone)."""
    zones = db.query(Zone).all()
    if not zones:
        return None

    closest_zone = None
    min_distance = float('inf')

    for z in zones:
        dist = haversine_distance(lat, lng, z.center_lat, z.center_lng)
        # If within zone radius, match immediately or pick the best
        if dist <= z.radius_km and dist < min_distance:
            min_distance = dist
            closest_zone = z

    # Fallback to closest zone if outside defined radius
    if not closest_zone:
        for z in zones:
            dist = haversine_distance(lat, lng, z.center_lat, z.center_lng)
            if dist < min_distance:
                min_distance = dist
                closest_zone = z

    return closest_zone

def update_zone_status_by_request_count(db: Session, zone: Zone, config: Optional[ZoneThresholdConfig] = None) -> Zone:
    """
    Business Rule (Mục 7.4):
    KHÔNG xác định mức độ khẩn cấp theo thời gian gửi yêu cầu của từng cá nhân.
    Xác định theo số lượng yêu cầu cứu trợ trong cùng một Zone.
    Ngưỡng số lượng cấu hình được bởi Admin:
    0 <= count < yellow_max  -> Zone Vàng (YELLOW): Cần hỗ trợ
    yellow_max <= count < orange_max -> Zone Cam (ORANGE): Nhu cầu hỗ trợ cao
    count >= red_min        -> Zone Đỏ (RED): Nhu cầu hỗ trợ rất cao
    """
    if not config:
        config = get_or_create_threshold_config(db)

    # Active emergency requests in this zone
    active_count = db.query(RescueRequest).filter(
        RescueRequest.zone_id == zone.id,
        RescueRequest.status.in_(["PENDING", "ACCEPTED", "IN_PROGRESS"])
    ).count()

    zone.request_count = active_count

    if active_count >= config.red_min:
        zone.status = "RED"
    elif active_count >= config.yellow_max:
        zone.status = "ORANGE"
    else:
        zone.status = "YELLOW"

    db.commit()
    db.refresh(zone)
    return zone

def process_rescue_request_zone(db: Session, request: RescueRequest) -> Tuple[Optional[Zone], str]:
    """
    Zone Engine Workflow (Mục 7.4):
    1. Người dân gửi Rescue Request.
    2. Hệ thống lấy vị trí GPS.
    3. Hệ thống xác định request thuộc Zone nào.
    4. Cập nhật số lượng request của Zone đó.
    5. Zone Engine so sánh số lượng với ngưỡng đã cấu hình.
    6. Cập nhật trạng thái Zone (Vàng/Cam/Đỏ).
    """
    zone = find_zone_for_coordinates(db, request.latitude, request.longitude)
    if not zone:
        return None, "YELLOW"

    request.zone_id = zone.id
    db.commit()

    config = get_or_create_threshold_config(db)
    updated_zone = update_zone_status_by_request_count(db, zone, config)
    return updated_zone, updated_zone.status

def recompute_all_zones(db: Session) -> list:
    """Recompute counts and statuses for all zones."""
    config = get_or_create_threshold_config(db)
    zones = db.query(Zone).all()
    updated_list = []
    for z in zones:
        updated = update_zone_status_by_request_count(db, z, config)
        updated_list.append(updated)
    return updated_list
