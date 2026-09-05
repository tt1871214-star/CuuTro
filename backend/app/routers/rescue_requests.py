import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.middleware.auth import get_current_user, require_role
from app.models.entities import RescueRequest, RescueTeam, User, Zone
from app.schemas.schemas import (
    RescueRequestCreate,
    RescueRequestResponse,
    RescueRequestStatusUpdate,
    RescueHistoryItem
)
from app.services.zone_engine import process_rescue_request_zone
from app.services.state_machine import transition_rescue_request
from app.routers.ws import ws_manager

router = APIRouter(prefix="/rescue-requests", tags=["Rescue Requests & Dispatch"])

def serialize_request(r: RescueRequest) -> RescueRequestResponse:
    histories_data = []
    if r.histories:
        for h in r.histories:
            histories_data.append(RescueHistoryItem(
                id=h.id,
                from_status=h.from_status,
                to_status=h.to_status,
                action=h.action,
                notes=h.notes,
                performed_by=h.performed_by,
                created_at=h.created_at
            ))

    return RescueRequestResponse(
        id=r.id,
        user_id=r.user_id,
        sender_name=r.sender_name or (r.user.full_name if r.user else "Người dân"),
        sender_phone=r.sender_phone or (r.user.phone if r.user else ""),
        zone_id=r.zone_id,
        zone_name=r.zone.name if r.zone else "Chưa phân vùng",
        zone_status=r.zone.status if r.zone else "YELLOW",
        relief_type=r.relief_type,
        personal_urgency=r.personal_urgency,
        description=r.description,
        image_url=r.image_url,
        latitude=r.latitude,
        longitude=r.longitude,
        status=r.status,
        assigned_team_id=r.assigned_team_id,
        assigned_team_name=r.assigned_team.team_name if r.assigned_team else None,
        created_at=r.created_at,
        updated_at=r.updated_at,
        histories=histories_data
    )

@router.post("", response_model=RescueRequestResponse)
async def submit_rescue_request(
    req: RescueRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(["PEOPLE", "ADMIN"]))
):
    """
    [Người dân] Gửi yêu cầu cứu trợ khẩn cấp (Mục 6.3.1 & 7.4).
    Tự động gắn vị trí GPS, loại hỗ trợ, mức khẩn cấp cá nhân, mô tả, ảnh minh chứng.
    Kích hoạt Zone Engine: xác định Zone, cập nhật số lượng yêu cầu,
    so sánh ngưỡng cấu hình để tự động chuyển mức Zone (Vàng / Cam / Đỏ),
    đồng thời phát cảnh báo thời gian thực lên Dashboard.
    """
    new_req = RescueRequest(
        user_id=user.id,
        sender_name=user.full_name,
        sender_phone=user.phone,
        relief_type=req.relief_type,
        personal_urgency=req.personal_urgency,
        description=req.description,
        image_url=req.image_url,
        latitude=req.latitude,
        longitude=req.longitude,
        status="PENDING"
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)

    # Trigger Zone Engine
    zone, zone_status = process_rescue_request_zone(db, new_req)

    # Broadcast to WebSocket
    await ws_manager.broadcast({
        "type": "NEW_RESCUE_REQUEST",
        "request": {
            "id": new_req.id,
            "sender_name": new_req.sender_name,
            "sender_phone": new_req.sender_phone,
            "relief_type": new_req.relief_type,
            "personal_urgency": new_req.personal_urgency,
            "latitude": new_req.latitude,
            "longitude": new_req.longitude,
            "zone_id": zone.id if zone else None,
            "zone_name": zone.name if zone else "Khu vực tự do",
            "zone_status": zone_status,
            "zone_count": zone.request_count if zone else 1,
            "status": new_req.status,
            "created_at": new_req.created_at.isoformat()
        }
    })

    return serialize_request(new_req)

@router.get("", response_model=List[RescueRequestResponse])
def get_rescue_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    zone_id: Optional[int] = None,
    relief_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["RESCUE_TEAM", "ADMIN"]))
):
    """[Đội cứu hộ / Admin] Lấy danh sách yêu cầu cứu trợ với các bộ lọc phục vụ điều phối."""
    query = db.query(RescueRequest)
    if status_filter:
        query = query.filter(RescueRequest.status == status_filter.upper())
    if zone_id:
        query = query.filter(RescueRequest.zone_id == zone_id)
    if relief_type:
        query = query.filter(RescueRequest.relief_type == relief_type)

    requests = query.order_by(RescueRequest.created_at.desc()).all()
    return [serialize_request(r) for r in requests]

@router.get("/my-requests", response_model=List[RescueRequestResponse])
def get_my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """[Người dân] Xem danh sách các yêu cầu cứu trợ của chính mình."""
    requests = db.query(RescueRequest).filter(
        RescueRequest.user_id == current_user.id
    ).order_by(RescueRequest.created_at.desc()).all()
    return [serialize_request(r) for r in requests]

@router.get("/my-active-status", response_model=Optional[RescueRequestResponse])
def get_my_active_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """[Người dân] Lấy yêu cầu cứu trợ đang xử lý gần nhất của người dùng."""
    active_req = db.query(RescueRequest).filter(
        RescueRequest.user_id == current_user.id,
        RescueRequest.status.in_(["PENDING", "ACCEPTED", "IN_PROGRESS"])
    ).order_by(RescueRequest.created_at.desc()).first()

    if not active_req:
        return None
    return serialize_request(active_req)

@router.get("/{id}", response_model=RescueRequestResponse)
def get_request_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Xem chi tiết một yêu cầu cứu trợ kèm lịch sử điều phối."""
    req = db.query(RescueRequest).filter(RescueRequest.id == id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Yêu cầu cứu trợ không tồn tại.")
    return serialize_request(req)

@router.put("/{id}/status", response_model=RescueRequestResponse)
async def update_request_status(
    id: int,
    update_data: RescueRequestStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["RESCUE_TEAM", "ADMIN"]))
):
    """
    [Đội cứu hộ / Admin] Chuyển đổi trạng thái xử lý theo State Machine (Mục 7.5):
    Pending -> Accepted -> In Progress -> Completed/Planned hoặc Cancelled.
    Backend từ chối các bước nhảy trạng thái tùy tiện.
    """
    req = db.query(RescueRequest).filter(RescueRequest.id == id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Yêu cầu cứu trợ không tồn tại.")

    updated_req = transition_rescue_request(
        db=db,
        request=req,
        target_status=update_data.status,
        user=current_user,
        notes=update_data.notes
    )

    # Broadcast state change
    await ws_manager.broadcast({
        "type": "REQUEST_STATUS_CHANGED",
        "request_id": updated_req.id,
        "new_status": updated_req.status,
        "assigned_team": updated_req.assigned_team.team_name if updated_req.assigned_team else None,
        "zone_id": updated_req.zone_id,
        "zone_count": updated_req.zone.request_count if updated_req.zone else 0,
        "zone_status": updated_req.zone.status if updated_req.zone else "YELLOW"
    })

    return serialize_request(updated_req)

@router.put("/{id}/citizen-cancel", response_model=RescueRequestResponse)
async def citizen_cancel_request(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """[Người dân] Hủy yêu cầu cứu trợ của chính mình nếu đã an toàn."""
    req = db.query(RescueRequest).filter(
        RescueRequest.id == id,
        RescueRequest.user_id == current_user.id
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu hoặc bạn không có quyền hủy.")

    if req.status in ["COMPLETED", "CANCELLED"]:
        raise HTTPException(status_code=400, detail=f"Yêu cầu đã ở trạng thái {req.status}, không thể hủy.")

    updated_req = transition_rescue_request(
        db=db,
        request=req,
        target_status="CANCELLED",
        user=current_user,
        notes="Người dân chủ động hủy yêu cầu (đã an toàn)."
    )

    await ws_manager.broadcast({
        "type": "REQUEST_STATUS_CHANGED",
        "request_id": updated_req.id,
        "new_status": "CANCELLED"
    })

    return serialize_request(updated_req)

@router.post("/upload-proof")
async def upload_proof_image(file: UploadFile = File(...)):
    """Upload ảnh minh chứng hiện trường cứu trợ."""
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận các file ảnh: jpg, jpeg, png, webp.")

    filename = f"proof_{uuid.uuid4().hex[:12]}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    return {
        "success": True,
        "filename": filename,
        "url": f"/api/uploads/{filename}"
    }
