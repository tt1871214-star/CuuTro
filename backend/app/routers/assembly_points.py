from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth import require_role
from app.models.entities import AssemblyPoint, User
from app.schemas.schemas import AssemblyPointResponse, AssemblyPointCreate

router = APIRouter(prefix="/assembly-points", tags=["Assembly Points & Shelters"])

@router.get("", response_model=List[AssemblyPointResponse])
def get_all_assembly_points(db: Session = Depends(get_db)):
    """Lấy danh sách các Điểm tập kết (Assembly) và Nơi trú ẩn an toàn (Refuge) trên bản đồ."""
    return db.query(AssemblyPoint).filter(AssemblyPoint.is_open == True).all()

@router.post("", response_model=AssemblyPointResponse)
def create_assembly_point(
    req: AssemblyPointCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """[Admin Only] Thêm một điểm tập kết hoặc nơi trú ẩn mới."""
    point = AssemblyPoint(
        name=req.name,
        point_type=req.point_type.upper(),
        address=req.address,
        latitude=req.latitude,
        longitude=req.longitude,
        capacity=req.capacity,
        contact_person=req.contact_person,
        contact_phone=req.contact_phone,
        is_open=req.is_open
    )
    db.add(point)
    db.commit()
    db.refresh(point)
    return point

@router.delete("/{id}")
def delete_assembly_point(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """[Admin Only] Xóa một điểm tập kết hoặc nơi trú ẩn."""
    point = db.query(AssemblyPoint).filter(AssemblyPoint.id == id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Điểm tập kết không tồn tại.")
    db.delete(point)
    db.commit()
    return {"success": True, "message": "Đã xóa điểm tập kết thành công."}
