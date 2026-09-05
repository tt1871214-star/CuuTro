from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.entities import CommunityPost, User
from app.schemas.schemas import (
    CommunityPostResponse,
    CommunityPostCreate,
    VerificationCreate
)
from app.services.community_service import verify_post_with_gps
from app.services.ai_service import ask_first_aid_ai

router = APIRouter(prefix="/community", tags=["Community Bulletin Board"])

class AIAssistantRequest(BaseModel):
    query: str

def serialize_post(p: CommunityPost) -> CommunityPostResponse:
    return CommunityPostResponse(
        id=p.id,
        user_id=p.user_id,
        author_name=p.author.full_name if p.author else "Ẩn danh",
        author_phone=p.author.phone if p.author else "",
        title=p.title,
        content=p.content,
        post_type=p.post_type,
        latitude=p.latitude,
        longitude=p.longitude,
        image_url=p.image_url,
        verification_status=p.verification_status,
        confirm_count=p.confirm_count or 0,
        deny_count=p.deny_count or 0,
        created_at=p.created_at,
        updated_at=p.updated_at
    )

@router.get("/posts", response_model=List[CommunityPostResponse])
def get_community_posts(db: Session = Depends(get_db)):
    """Lấy danh sách tin tức thực địa do cộng đồng chia sẻ."""
    posts = db.query(CommunityPost).order_by(CommunityPost.created_at.desc()).limit(100).all()
    return [serialize_post(p) for p in posts]

@router.post("/posts", response_model=CommunityPostResponse)
def create_community_post(
    req: CommunityPostCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Người dân đăng tin thực tế (đường ngập, cầu sập, mất điện, điểm trú ẩn, tình trạng giao thông)."""
    post = CommunityPost(
        user_id=user.id,
        title=req.title,
        content=req.content,
        post_type=req.post_type.upper(),
        latitude=req.latitude,
        longitude=req.longitude,
        image_url=req.image_url,
        verification_status="UNVERIFIED",
        confirm_count=0,
        deny_count=0
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return serialize_post(post)

@router.post("/posts/{id}/verify", response_model=CommunityPostResponse)
def verify_post(
    id: int,
    req: VerificationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Xác minh thông tin cộng đồng:
    Yêu cầu người xác nhận đang ở trong bán kính < 5km so với tọa độ bài đăng.
    Đạt 3 xác nhận đúng -> Tự động đánh dấu ĐÃ XÁC THỰC (VERIFIED).
    """
    updated_post = verify_post_with_gps(
        db=db,
        post_id=id,
        user=user,
        is_confirm=req.is_confirm,
        user_lat=req.current_lat,
        user_lng=req.current_lng
    )
    return serialize_post(updated_post)

@router.post("/ai-assistant")
def call_ai_assistant(req: AIAssistantRequest):
    """Trợ lý AI hỗ trợ xử lý thông tin và kỹ năng sơ cứu khẩn cấp (Mục 6.3.3)."""
    return ask_first_aid_ai(req.query)
