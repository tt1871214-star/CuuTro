# 🚨 CỨU TRỢ — Community Disaster Alert and Relief Platform

Nền tảng **CỨU TRỢ** là hệ thống cảnh báo thiên tai và điều phối cứu hộ cộng đồng theo thời gian thực. Ứng dụng được thiết kế chuyên dụng cho các tình huống thiên tai khẩn cấp (ngập lụt, bão lũ, sạt lở đất), cung cấp kênh liên lạc thông suốt giữa Người dân gặp nạn, Đội phản ứng cứu hộ và Ban chỉ huy phòng chống thiên tai (Admin).

Dự án bám sát toàn diện tài liệu đặc tả kỹ thuật **Capstone Project Proposal v1.0**, tuân thủ nghiêm ngặt nguyên tắc **hai project độc lập hoàn toàn** (`frontend/` và `backend/`).

---

## 🏗️ 1. Kiến Trúc Hệ Thống (Phân Tách Độc Lập)

```
cuu-tro/
├── backend/                     # Project REST API độc lập (Python FastAPI)
│   ├── app/
│   │   ├── core/                # Database, config (.env), security (JWT, Bcrypt)
│   │   ├── middleware/          # JWT auth & RBAC (People, RescueTeam, Admin)
│   │   ├── models/              # SQLAlchemy ORM (14 bảng quan hệ chuẩn hóa)
│   │   ├── schemas/             # Pydantic v2 validation & OpenAPI models
│   │   ├── services/            # Zone Engine, State Machine, Open-Meteo, Community, AI
│   │   ├── routers/             # 12 modules API Endpoints + WebSocket hub
│   │   ├── seed/                # Script khởi tạo dữ liệu mẫu (seed_data.py)
│   │   └── main.py              # Entrypoint FastAPI, CORS, Lifespan
│   ├── requirements.txt         # Thư viện phụ thuộc Python
│   ├── .env.example             # Cấu hình mẫu môi trường backend
│   └── Dockerfile               # Container backend
├── frontend/                    # Project Web Client độc lập (React Vite SPA)
│   ├── src/
│   │   ├── components/          # MapComponent (Leaflet), SOSModal, Banner Open-Meteo, Drawer
│   │   ├── context/             # AuthContext (RBAC), RealtimeContext (WebSocket)
│   │   ├── pages/
│   │   │   ├── Home.jsx         # [Luồng Người Dân] Bản đồ Zone, Nút SOS khẩn cấp, AI Sơ cứu
│   │   │   ├── CommunityBoard.jsx # Bảng tin thực địa, xác minh bán kính 5km
│   │   │   ├── FamilySafety.jsx # Nhật ký "Tôi an toàn"
│   │   │   ├── RescueTeamPortal.jsx # [Luồng Đội Cứu Hộ] Cổng điều phối, chuyển trạng thái State Machine
│   │   │   ├── AdminDashboard.jsx   # [Luồng Quản Trị] Cấu hình ngưỡng Zone Engine, User, Hotline
│   │   │   ├── Login.jsx        # Đăng nhập đa vai trò (kèm nút test nhanh)
│   │   │   └── Register.jsx     # Đăng ký Người dân & Đội cứu hộ
│   │   ├── services/api.js      # Axios client kết nối REST API qua VITE_API_BASE_URL
│   │   └── App.jsx              # Router & Role-based Protected Routes
│   ├── package.json
│   ├── vite.config.js           # Cấu hình proxy API & WebSocket
│   ├── .env.example             # Cấu hình mẫu môi trường frontend
│   └── Dockerfile               # Multi-stage build Nginx container
├── docker-compose.yml           # Triển khai đồng thời 3 container (Frontend, Backend, MySQL 8.0)
├── schema.sql                   # Schema MySQL chuẩn mực
└── README.md                    # Tài liệu hướng dẫn sử dụng & vận hành
```

---

## 👥 2. Ma Trận Phân Quyền Người Dùng (Mục 7.1)

Hệ thống phân quyền nghiêm ngặt qua JWT Middleware ở Backend (`backend/app/middleware/auth.py`):

| Chức năng | Người dân (PEOPLE) | Đội cứu hộ (RESCUE_TEAM) | Quản trị viên (ADMIN) |
|---|:---:|:---:|:---:|
| **Đăng ký tài khoản** | ✓ | ✓ *(Kèm hồ sơ đội)* | ✗ *(Cấp phát nội bộ)* |
| **Đăng nhập** | ✓ | ✓ | ✓ |
| **Gửi yêu cầu cứu trợ (SOS)** | ✓ | ✗ | ✗ |
| **Nhận & xử lý yêu cầu (Dispatch)** | ✗ | ✓ | ✓ |
| **Xem phân vùng Zone** | ✓ | ✓ | ✓ |
| **Cấu hình ngưỡng số lượng Zone** | ✗ | ✗ | ✓ |
| **Quản lý phân vùng Zone (CRUD)** | ✗ | ✗ | ✓ |
| **Quản lý người dùng & Đội cứu hộ** | ✗ | ✗ | ✓ |
| **Quản lý hệ thống & Đồng bộ Open-Meteo** | ✗ | ✗ | ✓ |

---

## ⚡ 3. Các Cơ Chế & Quy Tắc Nghiệp Vụ Cốt Lõi

### A. Zone Engine — Xác Định Mức Zone Động (Mục 7.4 - QUAN TRỌNG)
- **Quy tắc**: Tuyệt đối **KHÔNG** tính mức độ khẩn cấp theo thời gian chờ của cá nhân. Mức Zone phụ thuộc vào **mật độ và số lượng yêu cầu cứu hộ tích lũy trong cùng phân vùng**.
- **Cấu hình ngưỡng động**: Ngưỡng số lượng được Admin cấu hình linh hoạt trên màn hình Quản trị (`AdminDashboard.jsx`), không hardcode trong source code:
  - `0 <= Số yêu cầu < yellow_max`: **Zone Vàng (Gold)** — Cần hỗ trợ
  - `yellow_max <= Số yêu cầu < orange_max`: **Zone Cam (Orange)** — Nhu cầu hỗ trợ cao
  - `Số yêu cầu >= red_min`: **Zone Đỏ (Red)** — Nhu cầu hỗ trợ rất cao / Nguy kịch
- **Quy trình xử lý tự động**:
  1. Người dân gửi yêu cầu cứu trợ (tự động đính kèm tọa độ GPS).
  2. Hệ thống tính khoảng cách Haversine và xác định yêu cầu thuộc Zone nào.
  3. Cập nhật số lượng yêu cầu của Zone.
  4. Zone Engine so sánh với cấu hình ngưỡng và cập nhật trạng thái Zone (Vàng / Cam / Đỏ).
  5. Phát thông điệp qua WebSocket để Dashboard cập nhật màu sắc tức thì.

### B. State Machine Quản Lý Trạng Thái Cứu Trợ (Mục 7.5)
Hệ thống quản lý trạng thái bằng máy trạng thái hữu hạn, ngăn chặn mọi bước nhảy trạng thái trái phép:
- `PENDING` (Chờ xử lý) $\rightarrow$ `ACCEPTED` (Đội cứu hộ tiếp nhận nhiệm vụ)
- `ACCEPTED` $\rightarrow$ `IN_PROGRESS` (Đội xuất kích ca nô / di chuyển tới hiện trường)
- `IN_PROGRESS` $\rightarrow$ `COMPLETED` (Hoàn thành nhiệm vụ cứu nạn)
- `ACCEPTED` / `IN_PROGRESS` $\rightarrow$ `CANCELLED` (Đội cứu hộ hủy $\rightarrow$ yêu cầu **tự động quay về `PENDING`** để đội khác tiếp tục ứng cứu).
- Mọi bước chuyển đều được ghi nhật ký truy vết đầy đủ trong bảng `rescue_histories`.

### C. Tích Hợp Khí Tượng Open-Meteo API (Mục 6.3.1)
- Trực tiếp gọi Open-Meteo API theo thời gian thực (nhiệt độ, lượng mưa mm, tốc độ gió km/h, mã WMO).
- Tự động phát cảnh báo cấp độ Cam / Đỏ trên bản đồ khi lượng mưa hoặc sức gió vượt ngưỡng nguy hiểm.

### D. Bảng Tin Thực Địa & Xác Minh Bán Kính 5km (Mục 6.3.2)
- Người dân chia sẻ sự cố thực tế (đường ngập, cầu sập, mất điện, điểm trú ẩn).
- Chỉ người dùng có GPS trong bán kính **< 5km** so với sự cố mới được bấm *Xác nhận đúng* hoặc *Báo tin sai*.
- Khi đạt 3 xác nhận đúng $\rightarrow$ tự động gắn nhãn `ĐÃ XÁC THỰC (VERIFIED)`.

---

## 🔑 4. Tài Khoản Kiểm Thử Mẫu (Đã Nạp Sẵn Trong Seed)

| Vai trò | Số điện thoại | Mật khẩu | Chức danh hiển thị |
|---|---|---|---|
| **Quản trị viên (Admin)** | `0901234567` | `admin123` | Ban Chỉ Huy Ứng Phó Thiên Tai |
| **Đội cứu hộ 1 (Rescue Team)** | `0912345678` | `rescue123` | Đội Xuồng Cứu Nạn Chuyên Nghiệp 114 |
| **Đội cứu hộ 2 (Rescue Team)** | `0934567890` | `rescue123` | Biệt Đội Ca Nô Cứu Hộ Cầu Giấy |
| **Người dân (Resident)** | `0987654321` | `citizen123` | Trần Thị Mai (Cư dân) |

*(Trên giao diện Đăng nhập có sẵn 3 nút "Đăng nhập nhanh" để kiểm thử tiện lợi).*

---

## 🚀 5. Hướng Dẫn Cài Đặt & Chạy Từng Phần Riêng Biệt

### Yêu Cầu Hệ Thống:
- Python 3.9+
- Node.js 18+ và npm
- (Tùy chọn) MySQL 8.0 hoặc Docker Desktop

---

### BƯỚC 1: Khởi Chạy Backend API (FastAPI)

1. Mở cửa sổ Terminal thứ nhất:
```bash
cd backend
```

2. Cài đặt các thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

3. Cấu hình biến môi trường (`.env`):
File `.env` đã được thiết lập sẵn. Mặc định hệ thống dùng SQLite (`relief.db`) để chạy thử nghiệm ngay lập tức. Nếu muốn kết nối MySQL 8.0, bạn chỉ cần sửa trong `backend/.env`:
```env
DATABASE_URL="mysql+pymysql://root:password@localhost:3306/relief_db"
```

4. Nạp dữ liệu khởi tạo (Seed Data):
```bash
python app/seed/seed_data.py
```

5. Khởi chạy máy chủ FastAPI với Uvicorn:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **API Server**: `http://localhost:8000`
- **Tài liệu Swagger UI tương tác**: `http://localhost:8000/docs`
- **Tài liệu ReDoc**: `http://localhost:8000/redoc`

---

### BƯỚC 2: Khởi Chạy Frontend (React Vite)

1. Mở cửa sổ Terminal thứ hai:
```bash
cd frontend
```

2. Cài đặt các gói phụ thuộc (nếu chưa cài):
```bash
npm install
```

3. Cấu hình file `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

4. Khởi chạy Vite Dev Server:
```bash
npm run dev
```

- **Ứng dụng Web**: Mở trình duyệt truy cập `http://localhost:3000`

---

### BƯỚC 3: Triển Khai Toàn Diện Với Docker Compose (Tùy Chọn)

Nếu máy bạn đã bật Docker Desktop, có thể khởi động toàn bộ hạ tầng 3 container (MySQL 8.0, FastAPI Backend, React Frontend Nginx) chỉ bằng một lệnh:
```bash
docker-compose up --build
```
