from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth import get_current_user, require_role
from app.models.entities import RescueTeam, User
from app.schemas.schemas import RescueTeamResponse, RescueTeamLocationUpdate

router = APIRouter(prefix="/rescue-teams", tags=["Rescue Teams Management"])

@router.get("", response_model=List[RescueTeamResponse])
def get_rescue_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["RESCUE_TEAM", "ADMIN"]))
):
    """[Đội cứu hộ / Admin] Lấy danh sách các đội cứu hộ đang trực."""
    return db.query(RescueTeam).all()

@router.put("/my-location", response_model=RescueTeamResponse)
def update_my_team_location(
    req: RescueTeamLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["RESCUE_TEAM"]))
):
    """[Đội cứu hộ] Cập nhật vị trí GPS thời gian thực và trạng thái sẵn sàng trực chiến."""
    team = current_user.rescue_team
    if not team:
        raise HTTPException(status_code=404, detail="Tài khoản này chưa được gắn với hồ sơ Đội cứu hộ.")

    team.current_lat = req.latitude
    team.current_lng = req.longitude
    if req.status:
        team.status = req.status.upper()

    db.commit()
    db.refresh(team)
    return team

@router.put("/{id}/status", response_model=RescueTeamResponse)
def update_team_status_by_admin(
    id: int,
    status_str: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """[Admin Only] Cập nhật trạng thái đội cứu hộ (ACTIVE / BUSY / INACTIVE)."""
    team = db.query(RescueTeam).filter(RescueTeam.id == id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Đội cứu hộ không tồn tại.")

    team.status = status_str.upper()
    db.commit()
    db.refresh(team)
    return team
