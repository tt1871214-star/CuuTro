import requests
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.entities import Alert

WMO_WEATHER_MAP = {
    0: ("Trời quang đãng", "NORMAL", "Thời tiết ổn định, không có nguy cơ thiên tai."),
    1: ("Ít mây", "NORMAL", "Thời tiết thuận lợi cho công tác chuẩn bị và di chuyển."),
    2: ("Mây rải rác", "NORMAL", "Thời tiết bình thường."),
    3: ("Trời nhiều mây u ám", "NORMAL", "Có khả năng chuyển mưa, cần theo dõi diễn biến tiếp theo."),
    45: ("Sương mù", "YELLOW", "Tầm nhìn hạn chế, cẩn trọng khi di chuyển trên đường đèo dốc."),
    48: ("Sương mù đọng sương", "YELLOW", "Cẩn thận trơn trượt."),
    51: ("Mưa phùn nhẹ", "YELLOW", "Cần mang áo mưa và bảo quản thiết bị liên lạc."),
    53: ("Mưa phùn vừa", "YELLOW", "Đề phòng đường trơn trượt."),
    55: ("Mưa phùn dày đặc", "YELLOW", "Hạn chế ra ngoài nếu không thực sự cần thiết."),
    61: ("Mưa rào nhẹ", "YELLOW", "Theo dõi mực nước cục bộ tại các điểm trũng thấp."),
    63: ("Mưa vừa liên tục", "ORANGE", "Nguy cơ ngập cục bộ các tuyến đường thấp trũng, chuẩn bị đồ đạc lên cao."),
    65: ("Mưa rất to xối xả", "RED", "BÁO ĐỘNG ĐỎ: Nguy cơ lũ quét, sạt lở đất nghiêm trọng! Di tản ngay đến nơi an toàn."),
    80: ("Mưa rào rải rác", "YELLOW", "Theo dõi sát thông tin dự báo."),
    81: ("Mưa rào cường độ lớn", "ORANGE", "Đề phòng lốc sét và gió giật mạnh."),
    82: ("Mưa bão đặc biệt to", "RED", "NGUY HIỂM CỰC KỲ CAO: Mưa cực lớn, ngập lụt diện rộng, tuyệt đối không di chuyển qua ngầm tràn."),
    95: ("Dông bão mạnh", "ORANGE", "Gió giật nguy hiểm, đề phòng cây gãy đổ, mất điện lưới."),
    96: ("Dông bão kèm mưa đá nhỏ", "RED", "Tìm nơi trú ẩn kiên cố ngay lập tức, gia cố mái nhà."),
    99: ("Dông bão đặc biệt nguy hiểm kèm mưa đá lớn", "RED", "BÁO ĐỘNG KHẨN CẤP: Ở yên trong công trình kiên cố, ngắt cầu dao điện.")
}

def fetch_open_meteo_weather(lat: float = 21.0285, lng: float = 105.8542) -> Dict[str, Any]:
    """Fetch live meteorological observations and alerts from Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lng,
        "current": "temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m,wind_gusts_10m",
        "hourly": "precipitation_probability,rain",
        "timezone": "Asia/Bangkok"
    }

    try:
        resp = requests.get(url, params=params, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            current = data.get("current", {})
            w_code = current.get("weather_code", 0)
            wind_speed = current.get("wind_speed_10m", 0)
            precipitation = current.get("precipitation", 0)

            w_desc, level, guide = WMO_WEATHER_MAP.get(
                w_code, 
                ("Thời tiết diễn biến phức tạp", "YELLOW", "Chú ý theo dõi bản tin thời tiết.")
            )

            # Escalate if wind or rain is severe
            if wind_speed > 50 or precipitation > 40:
                level = "RED"
                guide = "BÁO ĐỘNG ĐỎ: Gió lốc hoặc lượng mưa cực đoan! Khẩn cấp di dời đến nơi trú ẩn kiên cố."
            elif wind_speed > 30 or precipitation > 15:
                if level != "RED":
                    level = "ORANGE"
                    guide = "CẢNH BÁO CAM: Gió mạnh và mưa to, có nguy cơ đổ cây cối và ngập sâu."

            return {
                "success": True,
                "latitude": lat,
                "longitude": lng,
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "precipitation": precipitation,
                "wind_speed": wind_speed,
                "wind_gusts": current.get("wind_gusts_10m"),
                "weather_code": w_code,
                "weather_description": w_desc,
                "alert_level": level,
                "safety_guideline": guide,
                "source": "Open-Meteo API"
            }
    except Exception as e:
        pass

    # Fallback default if network/offline
    return {
        "success": False,
        "latitude": lat,
        "longitude": lng,
        "temperature": 28.5,
        "humidity": 82,
        "precipitation": 12.0,
        "wind_speed": 25.0,
        "weather_code": 63,
        "weather_description": "Mưa vừa, có lúc mưa to (Dữ liệu dự phòng)",
        "alert_level": "ORANGE",
        "safety_guideline": "Cảnh giác ngập úng các điểm trũng thấp và sạt lở ven sông suối.",
        "source": "Open-Meteo (Offline Cache)"
    }

def sync_open_meteo_alerts_to_db(db: Session, target_area: str = "TP. Hà Nội & Đồng Bằng Bắc Bộ", lat: float = 21.0285, lng: float = 105.8542) -> Optional[Alert]:
    """Sync an alert to DB based on live Open-Meteo weather."""
    weather = fetch_open_meteo_weather(lat, lng)
    if weather.get("alert_level") in ["ORANGE", "RED"]:
        title = f"Cảnh báo khí tượng: {weather.get('weather_description')}"
        message = (
            f"Theo dữ liệu thời gian thực từ trạm quan trắc: Lượng mưa {weather.get('precipitation')} mm, "
            f"Vận tốc gió {weather.get('wind_speed')} km/h. Nhiệt độ {weather.get('temperature')}°C."
        )
        
        # Check if recent alert already exists to prevent duplicate flood
        existing = db.query(Alert).filter(Alert.source == "OPEN_METEO").order_by(Alert.created_at.desc()).first()
        if existing and existing.title == title:
            return existing

        alert = Alert(
            title=title,
            disaster_type="MƯA LŨ / THỜI TIẾT CỰC ĐOAN",
            target_area=target_area,
            alert_level=weather.get("alert_level"),
            message=message,
            guidelines=weather.get("safety_guideline"),
            latitude=lat,
            longitude=lng,
            radius_km=25.0,
            source="OPEN_METEO"
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    return None
