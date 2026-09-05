from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.entities import RescueRequest, RescueHistory, RescueTeam, User
from app.services.zone_engine import update_zone_status_by_request_count

VALID_TRANSITIONS = {
    "PENDING": ["ACCEPTED", "CANCELLED"],
    "ACCEPTED": ["IN_PROGRESS", "CANCELLED"],
    "IN_PROGRESS": ["COMPLETED", "CANCELLED"],
    "COMPLETED": [], # Final state
    "CANCELLED": ["PENDING"] # Allowed to reopen if needed
}

def transition_rescue_request(
    db: Session,
    request: RescueRequest,
    target_status: str,
    user: User,
    assigned_team_id: Optional[int] = None,
    notes: Optional[str] = None
) -> RescueRequest:
    current_status = request.status.upper() if request.status else "PENDING"
    target_status = target_status.upper()

    allowed = VALID_TRANSITIONS.get(current_status, [])
    if target_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể chuyển trạng thái từ '{current_status}' sang '{target_status}'. Các trạng thái cho phép: {allowed}."
        )

    # Specific business rules
    previous_team_id = request.assigned_team_id

    if target_status == "ACCEPTED":
        # Must have an assigned team
        if assigned_team_id:
            request.assigned_team_id = assigned_team_id
        elif user.rescue_team:
            request.assigned_team_id = user.rescue_team.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cần chỉ định đội cứu hộ tiếp nhận yêu cầu."
            )
        request.status = "ACCEPTED"
        action = "TIẾP NHẬN YÊU CẦU"

    elif target_status == "IN_PROGRESS":
        request.status = "IN_PROGRESS"
        action = "ĐANG TRIỂN KHAI CỨU HỘ"

    elif target_status == "COMPLETED":
        request.status = "COMPLETED"
        action = "HOÀN THÀNH CỨU HỘ"

    elif target_status == "CANCELLED":
        # If cancelled by rescue team, return to PENDING so another team can help!
        if user.role.name == "RESCUE_TEAM":
            request.status = "PENDING"
            request.assigned_team_id = None
            action = "ĐỘI CỨU HỘ HỦY NHIỆM VỤ - TRẢ VỀ HÀNG ĐỢI"
            target_status = "PENDING" # reset back
        else:
            # Cancelled by citizen or admin
            request.status = "CANCELLED"
            action = "HỦY YÊU CẦU CỨU TRỢ"

    # Save history
    history = RescueHistory(
        request_id=request.id,
        from_status=current_status,
        to_status=target_status,
        action=action,
        notes=notes or f"Thực hiện bởi {user.full_name} ({user.role.name})",
        performed_by=user.id
    )
    db.add(history)
    db.commit()
    db.refresh(request)

    # Recalculate zone status after state transition
    if request.zone:
        update_zone_status_by_request_count(db, request.zone)

    return request
