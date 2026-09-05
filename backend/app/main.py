import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.services.zone_engine import get_or_create_threshold_config

# Import routers
from app.routers import (
    auth,
    zones,
    rescue_requests,
    alerts,
    assembly_points,
    community,
    safe,
    emergency_contacts,
    rescue_teams,
    users,
    dashboard,
    ws
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if not exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        get_or_create_threshold_config(db)
    finally:
        db.close()
    yield
    # Shutdown: clean up if needed

app = FastAPI(
    title="CỨU TRỢ — Community Disaster Alert and Relief Platform API",
    description=(
        "Hệ thống API điều phối cứu hộ và cảnh báo thiên tai cộng đồng thời gian thực.\n\n"
        "- **Kiến trúc**: REST API độc lập với FastAPI, tự động sinh tài liệu Swagger UI và ReDoc.\n"
        "- **Phân quyền**: RBAC với 3 nhóm người dùng (Người dân, Đội cứu hộ, Quản trị viên).\n"
        "- **Zone Engine**: Phân vùng tự động theo GPS, xác định mức Vàng/Cam/Đỏ dựa trên số lượng yêu cầu và ngưỡng cấu hình linh hoạt.\n"
        "- **State Machine**: Kiểm soát nghiêm ngặt luồng trạng thái Pending -> Accepted -> In Progress -> Completed/Cancelled.\n"
        "- **Open-Meteo**: Tích hợp dữ liệu quan trắc thời tiết và cảnh báo rủi ro khí tượng theo thời gian thực."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for proof images
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers with /api prefix
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(zones.router, prefix=settings.API_V1_STR)
app.include_router(rescue_requests.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(assembly_points.router, prefix=settings.API_V1_STR)
app.include_router(community.router, prefix=settings.API_V1_STR)
app.include_router(safe.router, prefix=settings.API_V1_STR)
app.include_router(emergency_contacts.router, prefix=settings.API_V1_STR)
app.include_router(rescue_teams.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(ws.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": "CỨU TRỢ — Community Disaster Alert and Relief Platform",
        "status": "online",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "version": "1.0.0"
    }
