from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth import require_role
from app.models.entities import User
from app.schemas.schemas import UserResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["Users Management"])

@router.get("", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """[Admin Only] Danh sách tất cả người dùng trong hệ thống (Người dân, Đội cứu hộ, Quản trị)."""
    users = db.query(User).order_by(User.id.desc()).all()
    results = []
    for u in users:
        results.append(UserResponse(
            id=u.id,
            phone=u.phone,
            full_name=u.full_name,
            role=u.role.name if u.role else "PEOPLE",
            is_active=u.is_active,
            created_at=u.created_at
        ))
    return results

@router.put("/{id}/status", response_model=UserResponse)
def toggle_user_status(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"]))
):
    """[Admin Only] Khóa hoặc mở khóa tài khoản người dùng."""
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại.")

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        phone=user.phone,
        full_name=user.full_name,
        role=user.role.name if user.role else "PEOPLE",
        is_active=user.is_active,
        created_at=user.created_at
    )
