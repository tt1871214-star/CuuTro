from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth import require_role
from app.models.entities import Alert, User
from app.schemas.schemas import AlertResponse, AlertCreate
from app.services.weather_service import fetch_open_meteo_weather, sync_open_meteo_alerts_to_db
from app.routers.ws import ws_manager

router = APIRouter(prefix="/alerts", tags=["Disaster Alerts & Open-Meteo"])

@router.get("", response_model=List[AlertResponse])
def get_active_alerts(db: Session = Depends(get_db)):
    """Lấy danh sách các cảnh báo thiên tai đang hiệu lực."""
    return db.query(Alert).order_by(Alert.created_at.desc()).limit(50).all()

@router.post("", response_model=AlertResponse)
async def create_alert(
    req: AlertCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """[Admin Only] Phát cảnh báo thiên tai khẩn cấp."""
    alert = Alert(
        title=req.title,
        disaster_type=req.disaster_type,
        target_area=req.target_area,
        alert_level=req.alert_level.upper(),
        message=req.message,
        guidelines=req.guidelines,
        latitude=req.latitude,
        longitude=req.longitude,
        radius_km=req.radius_km or 15.0,
        source="MANUAL"
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    # Broadcast alert
    await ws_manager.broadcast({
        "type": "NEW_ALERT",
        "alert": {
            "id": alert.id,
            "title": alert.title,
            "level": alert.alert_level,
            "message": alert.message,
            "target_area": alert.target_area,
            "created_at": alert.created_at.isoformat()
        }
    })

    return alert

@router.get("/weather-live")
def get_live_weather(
    lat: float = Query(21.0285, description="Vĩ độ"),
    lng: float = Query(105.8542, description="Kinh độ")
):
    """Lấy thông tin thời tiết & mức độ rủi ro trực tiếp từ Open-Meteo API theo tọa độ."""
    return fetch_open_meteo_weather(lat, lng)

@router.post("/weather-sync", response_model=Optional[AlertResponse])
async def sync_weather_alert(
    area: str = Query("Hà Nội & Bắc Bộ"),
    lat: float = Query(21.0285),
    lng: float = Query(105.8542),
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """[Admin Only] Đồng bộ cảnh báo thiên tai tự động từ dữ liệu Open-Meteo vào hệ thống."""
    alert = sync_open_meteo_alerts_to_db(db, area, lat, lng)
    if alert:
        await ws_manager.broadcast({
            "type": "NEW_ALERT",
            "alert": {
                "id": alert.id,
                "title": alert.title,
                "level": alert.alert_level,
                "message": alert.message,
                "target_area": alert.target_area,
                "created_at": alert.created_at.isoformat()
            }
        })
    return alert
