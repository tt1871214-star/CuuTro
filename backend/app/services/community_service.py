from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.entities import CommunityPost, CommunityVerification, User
from app.services.zone_engine import haversine_distance

MAX_VERIFY_DISTANCE_KM = 5.0

def verify_post_with_gps(
    db: Session,
    post_id: int,
    user: User,
    is_confirm: bool,
    user_lat: float,
    user_lng: float
) -> CommunityPost:
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bài đăng không tồn tại."
        )

    if post.user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bạn không thể tự xác thực bài đăng của chính mình."
        )

    # Check previous verification
    existing = db.query(CommunityVerification).filter(
        CommunityVerification.post_id == post_id,
        CommunityVerification.user_id == user.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bạn đã biểu quyết xác thực bài viết này rồi."
        )

    # Check GPS distance
    distance = haversine_distance(user_lat, user_lng, post.latitude, post.longitude)
    if distance > MAX_VERIFY_DISTANCE_KM:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Khoảng cách GPS hiện tại của bạn cách điểm xảy ra sự cố {distance:.2f} km (vượt quá giới hạn cho phép {MAX_VERIFY_DISTANCE_KM} km để xác minh thực địa)."
        )

    # Record verification
    verification = CommunityVerification(
        post_id=post.id,
        user_id=user.id,
        is_confirm=is_confirm,
        distance_km=round(distance, 2)
    )
    db.add(verification)

    if is_confirm:
        post.confirm_count = (post.confirm_count or 0) + 1
    else:
        post.deny_count = (post.deny_count or 0) + 1

    # Status update rules
    if post.confirm_count >= 3:
        post.verification_status = "VERIFIED"
    elif post.deny_count >= 3:
        post.verification_status = "REJECTED"

    db.commit()
    db.refresh(post)
    return post
