from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth import require_role
from app.models.entities import EmergencyContact, User
from app.schemas.schemas import EmergencyContactResponse, EmergencyContactCreate

router = APIRouter(prefix="/emergency-contacts", tags=["Emergency Hotlines"])

@router.get("", response_model=List[EmergencyContactResponse])
def get_emergency_contacts(db: Session = Depends(get_db)):
    """Danh bạ khẩn cấp toàn quốc (112, 114, 115, hotline địa phương)."""
    return db.query(EmergencyContact).filter(EmergencyContact.is_active == True).order_by(EmergencyContact.sort_order.asc()).all()

@router.post("", response_model=EmergencyContactResponse)
def create_emergency_contact(
    req: EmergencyContactCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """[Admin Only] Thêm đầu số khẩn cấp mới."""
    contact = EmergencyContact(
        name=req.name,
        phone=req.phone,
        description=req.description,
        icon_type=req.icon_type,
        sort_order=req.sort_order,
        is_active=req.is_active
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/{id}")
def delete_emergency_contact(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """[Admin Only] Xóa đầu số khẩn cấp."""
    c = db.query(EmergencyContact).filter(EmergencyContact.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy số liên hệ.")
    db.delete(c)
    db.commit()
    return {"success": True, "message": "Đã xóa số liên hệ khẩn cấp."}
