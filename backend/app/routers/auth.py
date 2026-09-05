from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.middleware.auth import get_current_user
from app.models.entities import User, Role, RescueTeam
from app.schemas.schemas import (
    LoginRequest, 
    CitizenRegisterRequest, 
    RescueTeamRegisterRequest, 
    TokenResponse, 
    UserResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_role_or_fail(db: Session, role_name: str) -> Role:
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = Role(name=role_name)
        db.add(role)
        db.commit()
        db.refresh(role)
    return role

@router.post("/register/citizen", response_model=TokenResponse)
def register_citizen(req: CitizenRegisterRequest, db: Session = Depends(get_db)):
    """Đăng ký tài khoản Người dân (People)."""
    existing = db.query(User).filter(User.phone == req.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số điện thoại này đã được đăng ký trong hệ thống."
        )

    role = get_role_or_fail(db, "PEOPLE")
    user = User(
        phone=req.phone,
        password_hash=get_password_hash(req.password),
        full_name=req.full_name,
        role_id=role.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": "PEOPLE"})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            phone=user.phone,
            full_name=user.full_name,
            role="PEOPLE",
            is_active=user.is_active,
            created_at=user.created_at
        )
    )

@router.post("/register/rescue-team", response_model=TokenResponse)
def register_rescue_team(req: RescueTeamRegisterRequest, db: Session = Depends(get_db)):
    """Đăng ký tài khoản Đội cứu hộ (Rescue Team)."""
    existing = db.query(User).filter(User.phone == req.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số điện thoại này đã được đăng ký trong hệ thống."
        )

    role = get_role_or_fail(db, "RESCUE_TEAM")
    user = User(
        phone=req.phone,
        password_hash=get_password_hash(req.password),
        full_name=req.full_name,
        role_id=role.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    team = RescueTeam(
        user_id=user.id,
        team_name=req.team_name,
        leader_name=req.leader_name,
        contact_phone=req.contact_phone,
        status="ACTIVE",
        current_lat=req.current_lat,
        current_lng=req.current_lng
    )
    db.add(team)
    db.commit()

    token = create_access_token({"sub": str(user.id), "role": "RESCUE_TEAM"})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            phone=user.phone,
            full_name=user.full_name,
            role="RESCUE_TEAM",
            is_active=user.is_active,
            created_at=user.created_at
        )
    )

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Đăng nhập chung cho cả 3 vai trò: Người dân, Đội cứu hộ, Admin."""
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Số điện thoại hoặc mật khẩu không chính xác."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị khóa."
        )

    role_name = user.role.name if user.role else "PEOPLE"
    token = create_access_token({"sub": str(user.id), "role": role_name})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            phone=user.phone,
            full_name=user.full_name,
            role=role_name,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Lấy thông tin tài khoản đang đăng nhập."""
    role_name = current_user.role.name if current_user.role else "PEOPLE"
    return UserResponse(
        id=current_user.id,
        phone=current_user.phone,
        full_name=current_user.full_name,
        role=role_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
