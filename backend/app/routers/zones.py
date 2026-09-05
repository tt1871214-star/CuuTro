from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth import get_current_user, require_role
from app.models.entities import Zone, ZoneThresholdConfig, User
from app.schemas.schemas import (
    ZoneResponse,
    ZoneCreate,
    ZoneUpdate,
    ZoneThresholdConfigResponse,
    ZoneThresholdConfigUpdate
)
from app.services.zone_engine import (
    get_or_create_threshold_config,
    recompute_all_zones,
    update_zone_status_by_request_count
)
from app.routers.ws import ws_manager

router = APIRouter(prefix="/zones", tags=["Zones & Zone Engine"])

@router.get("", response_model=List[ZoneResponse])
def get_all_zones(db: Session = Depends(get_db)):
    """Lấy danh sách tất cả các Zone cùng trạng thái (Vàng / Cam / Đỏ) và số lượng yêu cầu."""
    return db.query(Zone).order_by(Zone.id.asc()).all()

@router.get("/config/thresholds", response_model=ZoneThresholdConfigResponse)
def get_zone_threshold_config(db: Session = Depends(get_db)):
    """Lấy cấu hình ngưỡng số lượng chuyển mức Zone hiện tại."""
    return get_or_create_threshold_config(db)

@router.put("/config/thresholds", response_model=ZoneThresholdConfigResponse)
async def update_zone_threshold_config(
    req: ZoneThresholdConfigUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """
    [Admin Only] Cấu hình ngưỡng số lượng chuyển mức Zone (Mục 7.4).
    Khi lưu, Zone Engine tự động tính toán lại toàn bộ trạng thái Zone
    và phát thông báo thời gian thực qua WebSocket.
    """
    if req.yellow_max >= req.orange_max or req.orange_max > req.red_min:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Giá trị ngưỡng không hợp lệ! Quy tắc bắt buộc: yellow_max < orange_max <= red_min."
        )

    config = get_or_create_threshold_config(db)
    config.yellow_max = req.yellow_max
    config.orange_max = req.orange_max
    config.red_min = req.red_min
    db.commit()
    db.refresh(config)

    # Recompute all zones based on newly configured thresholds
    updated_zones = recompute_all_zones(db)

    # Broadcast realtime event
    await ws_manager.broadcast({
        "type": "ZONE_CONFIG_UPDATED",
        "thresholds": {
            "yellow_max": config.yellow_max,
            "orange_max": config.orange_max,
            "red_min": config.red_min
        },
        "zones": [{"id": z.id, "name": z.name, "count": z.request_count, "status": z.status} for z in updated_zones]
    })

    return config

@router.post("", response_model=ZoneResponse)
def create_zone(
    req: ZoneCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """[Admin Only] Tạo một phân vùng Zone mới."""
    existing = db.query(Zone).filter(Zone.code == req.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã Zone '{req.code}' đã tồn tại."
        )

    zone = Zone(
        code=req.code,
        name=req.name,
        description=req.description,
        center_lat=req.center_lat,
        center_lng=req.center_lng,
        radius_km=req.radius_km,
        request_count=0,
        status="YELLOW"
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone

@router.put("/{id}", response_model=ZoneResponse)
def update_zone(
    id: int,
    req: ZoneUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """[Admin Only] Cập nhật thông tin phân vùng Zone."""
    zone = db.query(Zone).filter(Zone.id == id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone không tồn tại.")

    if req.name is not None:
        zone.name = req.name
    if req.description is not None:
        zone.description = req.description
    if req.radius_km is not None:
        zone.radius_km = req.radius_km
    if req.center_lat is not None:
        zone.center_lat = req.center_lat
    if req.center_lng is not None:
        zone.center_lng = req.center_lng

    db.commit()
    db.refresh(zone)
    return zone

@router.delete("/{id}")
def delete_zone(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """[Admin Only] Xóa phân vùng Zone."""
    zone = db.query(Zone).filter(Zone.id == id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone không tồn tại.")
    db.delete(zone)
    db.commit()
    return {"success": True, "message": f"Đã xóa Zone {zone.name} thành công."}

@router.post("/recompute")
async def trigger_recompute_zones(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """[Admin Only] Buộc Zone Engine tính toán lại tất cả các Zone."""
    updated_zones = recompute_all_zones(db)
    await ws_manager.broadcast({
        "type": "ZONES_RECOMPUTED",
        "zones": [{"id": z.id, "name": z.name, "count": z.request_count, "status": z.status} for z in updated_zones]
    })
    return {"success": True, "message": f"Đã tính toán lại {len(updated_zones)} vùng Zone."}
