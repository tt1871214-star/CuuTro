from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import RescueRequest, Zone, RescueTeam, AssemblyPoint, Alert
from app.schemas.schemas import DashboardOverviewResponse, AlertResponse

router = APIRouter(prefix="/dashboard", tags=["Emergency Dashboard Metrics"])

@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(db: Session = Depends(get_db)):
    """
    Emergency Dashboard (Mục 7.6):
    Tổng hợp chỉ số thời gian thực: tổng số yêu cầu, số đang chờ, đang xử lý,
    đã hoàn thành, phân bố số lượng Zone theo màu Vàng/Cam/Đỏ, đội cứu hộ đang trực.
    """
    total = db.query(RescueRequest).count()
    pending = db.query(RescueRequest).filter(RescueRequest.status == "PENDING").count()
    accepted = db.query(RescueRequest).filter(RescueRequest.status == "ACCEPTED").count()
    in_progress = db.query(RescueRequest).filter(RescueRequest.status == "IN_PROGRESS").count()
    completed = db.query(RescueRequest).filter(RescueRequest.status == "COMPLETED").count()
    cancelled = db.query(RescueRequest).filter(RescueRequest.status == "CANCELLED").count()

    yellow_zones = db.query(Zone).filter(Zone.status == "YELLOW").count()
    orange_zones = db.query(Zone).filter(Zone.status == "ORANGE").count()
    red_zones = db.query(Zone).filter(Zone.status == "RED").count()

    active_teams = db.query(RescueTeam).filter(RescueTeam.status == "ACTIVE").count()
    open_shelters = db.query(AssemblyPoint).filter(AssemblyPoint.is_open == True).count()

    latest_alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(5).all()

    return DashboardOverviewResponse(
        total_requests=total,
        pending_requests=pending,
        accepted_requests=accepted,
        in_progress_requests=in_progress,
        completed_requests=completed,
        cancelled_requests=cancelled,
        yellow_zones_count=yellow_zones,
        orange_zones_count=orange_zones,
        red_zones_count=red_zones,
        active_teams_count=active_teams,
        open_shelters_count=open_shelters,
        latest_alerts=latest_alerts
    )
