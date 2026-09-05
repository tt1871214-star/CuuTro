from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# AUTH & USER
class LoginRequest(BaseModel):
    phone: str
    password: str

class CitizenRegisterRequest(BaseModel):
    phone: str
    password: str
    full_name: str

class RescueTeamRegisterRequest(BaseModel):
    phone: str
    password: str
    full_name: str
    team_name: str
    leader_name: str
    contact_phone: str
    current_lat: float = 21.0285
    current_lng: float = 105.8542

class UserResponse(BaseModel):
    id: int
    phone: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

# RESCUE TEAM
class RescueTeamResponse(BaseModel):
    id: int
    user_id: int
    team_name: str
    leader_name: str
    contact_phone: str
    status: str
    current_lat: float
    current_lng: float
    assigned_zone_id: Optional[int] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class RescueTeamLocationUpdate(BaseModel):
    latitude: float
    longitude: float
    status: Optional[str] = None

# ZONE
class ZoneResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    center_lat: float
    center_lng: float
    radius_km: float
    request_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ZoneCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    center_lat: float
    center_lng: float
    radius_km: float = 5.0

class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    radius_km: Optional[float] = None
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None

class ZoneThresholdConfigResponse(BaseModel):
    id: int
    yellow_max: int
    orange_max: int
    red_min: int
    description: str
    updated_at: datetime

    class Config:
        from_attributes = True

class ZoneThresholdConfigUpdate(BaseModel):
    yellow_max: int = Field(..., ge=1, description="Ngưỡng trên của Zone Vàng")
    orange_max: int = Field(..., ge=2, description="Ngưỡng trên của Zone Cam")
    red_min: int = Field(..., ge=2, description="Ngưỡng dưới của Zone Đỏ (>= red_min)")

# RESCUE REQUEST
class RescueRequestCreate(BaseModel):
    relief_type: str = "CỨU NGƯỜI MẮC KẸT"
    personal_urgency: str = "CAO"
    description: Optional[str] = None
    latitude: float
    longitude: float
    image_url: Optional[str] = None

class RescueRequestStatusUpdate(BaseModel):
    status: str # ACCEPTED, IN_PROGRESS, COMPLETED, CANCELLED
    notes: Optional[str] = None

class RescueRequestAssign(BaseModel):
    team_id: int
    notes: Optional[str] = None

class RescueHistoryItem(BaseModel):
    id: int
    from_status: Optional[str]
    to_status: str
    action: str
    notes: Optional[str]
    performed_by: int
    created_at: datetime

    class Config:
        from_attributes = True

class RescueRequestResponse(BaseModel):
    id: int
    user_id: int
    sender_name: Optional[str] = None
    sender_phone: Optional[str] = None
    zone_id: Optional[int] = None
    zone_name: Optional[str] = None
    zone_status: Optional[str] = None
    relief_type: str
    personal_urgency: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    latitude: float
    longitude: float
    status: str
    assigned_team_id: Optional[int] = None
    assigned_team_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    histories: Optional[List[RescueHistoryItem]] = None

    class Config:
        from_attributes = True

# ALERT
class AlertCreate(BaseModel):
    title: str
    disaster_type: str = "BÃO / MƯA LŨ"
    target_area: str
    alert_level: str = "ORANGE"
    message: str
    guidelines: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = 15.0

class AlertResponse(BaseModel):
    id: int
    title: str
    disaster_type: str
    target_area: str
    alert_level: str
    message: str
    guidelines: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: float
    source: str
    created_at: datetime

    class Config:
        from_attributes = True

# ASSEMBLY POINT
class AssemblyPointCreate(BaseModel):
    name: str
    point_type: str = "ASSEMBLY"
    address: str
    latitude: float
    longitude: float
    capacity: int = 100
    current_occupancy: int = 0
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    is_open: bool = True

class AssemblyPointResponse(BaseModel):
    id: int
    name: str
    point_type: str
    address: str
    latitude: float
    longitude: float
    capacity: int
    current_occupancy: int
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    is_open: bool
    created_at: datetime

    class Config:
        from_attributes = True

# COMMUNITY POST & VERIFICATION
class CommunityPostCreate(BaseModel):
    title: str
    content: str
    post_type: str = "FLOOD"
    latitude: float
    longitude: float
    image_url: Optional[str] = None

class VerificationCreate(BaseModel):
    is_confirm: bool # True = xác nhận đúng, False = báo tin sai
    current_lat: float
    current_lng: float

class CommunityPostResponse(BaseModel):
    id: int
    user_id: int
    author_name: Optional[str] = None
    author_phone: Optional[str] = None
    title: str
    content: str
    post_type: str
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    verification_status: str
    confirm_count: int
    deny_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# SAFE STATUS
class SafeStatusCreate(BaseModel):
    latitude: float
    longitude: float
    status_message: Optional[str] = "Tôi an toàn"
    battery_level: Optional[int] = None

class SafeStatusResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    latitude: float
    longitude: float
    status_message: str
    battery_level: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# EMERGENCY CONTACT
class EmergencyContactResponse(BaseModel):
    id: int
    name: str
    phone: str
    description: Optional[str] = None
    icon_type: str
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True

class EmergencyContactCreate(BaseModel):
    name: str
    phone: str
    description: Optional[str] = None
    icon_type: str = "phone"
    sort_order: int = 0
    is_active: bool = True

# DASHBOARD
class DashboardOverviewResponse(BaseModel):
    total_requests: int
    pending_requests: int
    accepted_requests: int
    in_progress_requests: int
    completed_requests: int
    cancelled_requests: int
    yellow_zones_count: int
    orange_zones_count: int
    red_zones_count: int
    active_teams_count: int
    open_shelters_count: int
    latest_alerts: List[AlertResponse]
