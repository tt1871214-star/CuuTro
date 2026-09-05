from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.entities import SafeStatus, User
from app.schemas.schemas import SafeStatusResponse, SafeStatusCreate

router = APIRouter(prefix="/safe", tags=["I Am Safe Feature"])

@router.post("/check-in", response_model=SafeStatusResponse)
def check_in_safe(
    req: SafeStatusCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Chức năng 'Tôi an toàn' (Mục 6.3.2):
    Nút xác nhận an toàn 1-chạm, lưu vị trí GPS và tin nhắn trấn an để người thân biết.
    """
    safe = SafeStatus(
        user_id=user.id,
        latitude=req.latitude,
        longitude=req.longitude,
        status_message=req.status_message or "Tôi an toàn",
        battery_level=req.battery_level
    )
    db.add(safe)
    db.commit()
    db.refresh(safe)

    return SafeStatusResponse(
        id=safe.id,
        user_id=safe.user_id,
        user_name=user.full_name,
        user_phone=user.phone,
        latitude=safe.latitude,
        longitude=safe.longitude,
        status_message=safe.status_message,
        battery_level=safe.battery_level,
        created_at=safe.created_at
    )

@router.get("/recent", response_model=List[SafeStatusResponse])
def get_recent_safe_statuses(db: Session = Depends(get_db)):
    """Lấy danh sách các thông báo 'Tôi an toàn' gần đây."""
    records = db.query(SafeStatus).order_by(SafeStatus.created_at.desc()).limit(50).all()
    results = []
    for r in records:
        results.append(SafeStatusResponse(
            id=r.id,
            user_id=r.user_id,
            user_name=r.user.full_name if r.user else "Người dùng",
            user_phone=r.user.phone if r.user else "",
            latitude=r.latitude,
            longitude=r.longitude,
            status_message=r.status_message,
            battery_level=r.battery_level,
            created_at=r.created_at
        ))
    return results
