# CodeArena - Nền Tảng Chấm Bài Tự Động & Quản Trị Người Dùng (RBAC)

## 🌟 Giới thiệu
Hệ thống website **CodeArena** (Đại học Công nghiệp Hà Nội - HaUI, Nhóm 14) được tích hợp trọn vẹn giữa:
- **Frontend**: Giao diện Sandbox IDE, Chấm điểm bài thi, Contest Arena, Kết quả AI, và **Portal Quản lý Tài khoản (Admin)** được xây dựng bằng Tailwind CSS, responsive, hiện đại.
- **Backend API**: Xây dựng bằng **FastAPI (Python 3.14)** và cơ sở dữ liệu **SQLite** (`codearena.db`), hỗ trợ đầy đủ xác thực bảo mật PBKDF2-SHA256, phân quyền RBAC và API RESTful CRUD tài khoản.

---

## 🚀 Hướng dẫn khởi chạy

### Cách 1: Chạy nhanh bằng 1-Click trên Windows
Nhấp đúp chuột vào file:
```
start.bat
```
File này sẽ tự động kiểm tra Python, cài đặt thư viện cần thiết và mở trình duyệt tại `http://localhost:8000`.

### Cách 2: Khởi chạy bằng dòng lệnh
```bash
# 1. Cài đặt thư viện (nếu chưa có)
python -m pip install -r requirements.txt

# 2. Khởi chạy server FastAPI
python run_server.py
```

- **Website CodeArena**: [http://localhost:8000](http://localhost:8000)
- **Tài liệu Swagger API (Interactive Docs)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Tài liệu ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🛡️ Danh sách tài khoản mẫu mặc định

| Vai trò (Role) | Họ và tên | Email | Mật khẩu | Mã ID | Quyền hạn |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Admin (Quản trị viên)** | Quản trị viên Hệ thống | `admin@haui.edu.vn` | `admin` | `ADMIN-01` | Toàn quyền Thêm, Sửa, Xóa, Khóa tài khoản, xem tất cả tính năng |
| **Giáo viên** | TS. Nguyễn Thị Hoa Huệ | `gv.huenth@haui.edu.vn` | `password123` | `GV-HAUI-01` | Chấm điểm bài thi, tạo kỳ thi, quản lý bài tập |
| **Sinh viên** | Hoàng Anh Tú | `20240606239@sv.haui.edu.vn` | `password123` | `20240606239` | Luyện tập Sandbox IDE, tham gia Contest, xem kết quả cá nhân |
| **Sinh viên** | Nguyễn Kim Huy | `20240606240@sv.haui.edu.vn` | `password123` | `20240606240` | Sinh viên thành viên |
| **Sinh viên** | Nguyễn Cảnh Hải | `20240606241@sv.haui.edu.vn` | `password123` | `20240606241` | Sinh viên thành viên |
| **Sinh viên** | Lưu Quang Huy | `20240606242@sv.haui.edu.vn` | `password123` | `20240606242` | Sinh viên thành viên |
| **Sinh viên** | Hoàng Thái Hưng | `20240606243@sv.haui.edu.vn` | `password123` | `20240606243` | Sinh viên thành viên |

*(Lưu ý: Bạn cũng có thể bấm nút **1-Click Test** trong cửa sổ Đăng nhập để chuyển đổi giữa các tài khoản mẫu ngay lập tức)*

---

## 🛠️ Cấu trúc thư mục Backend

```
d:\Arenacode\
├── backend/
│   ├── __init__.py
│   ├── auth.py          # Hàm băm mật khẩu PBKDF2-HMAC-SHA256, kiểm tra mật khẩu, tạo avatar
│   ├── database.py      # Kết nối SQLite, khởi tạo bảng users, seed dữ liệu mẫu, các hàm CRUD
│   ├── models.py        # Pydantic schemas (UserCreate, UserUpdate, UserResponse, LoginRequest,...)
│   └── main.py          # FastAPI app, CORS middleware, các REST API endpoints và phục vụ Frontend
├── codearena.db         # Cơ sở dữ liệu SQLite lưu trữ người dùng
├── index.html           # Toàn bộ giao diện Frontend CodeArena và Admin Portal
├── requirements.txt     # Danh sách thư viện Python
├── run_server.py        # File chạy máy chủ FastAPI (Port 8000)
└── start.bat            # Script khởi động 1-click cho Windows
```

---

## 📡 Danh sách RESTful API Endpoints

### 1. Xác thực & Thống kê
- `GET /api/health`: Kiểm tra trạng thái máy chủ và kết nối SQLite.
- `GET /api/stats`: Thống kê tổng quan số lượng tài khoản (Admin, Giáo viên, Sinh viên, Trạng thái).
- `POST /api/auth/login`: Đăng nhập bằng Email và Mật khẩu (kiểm tra tài khoản khóa, cấp session token).

### 2. Quản lý Tài khoản (Admin CRUD)
- `GET /api/users`: Lấy danh sách người dùng (hỗ trợ tìm kiếm theo từ khóa `q`, lọc theo `role`, lọc theo `status`).
- `GET /api/users/{user_id}`: Xem chi tiết thông tin một tài khoản.
- `POST /api/users`: Tạo mới tài khoản (kiểm tra trùng mã ID, trùng email, mã hóa mật khẩu bảo mật).
- `PUT /api/users/{user_id}`: Chỉnh sửa thông tin (tên, email, vai trò, trạng thái, đổi mật khẩu mới).
- `DELETE /api/users/{user_id}`: Xóa vĩnh viễn tài khoản (có cơ chế bảo vệ: không cho phép xóa tài khoản Admin gốc `ADMIN-01` hoặc tự xóa chính mình).
- `POST /api/users/{user_id}/toggle-status`: Bật/tắt trạng thái Khóa (`locked`) hoặc Hoạt động (`active`).
- `POST /api/users/{user_id}/reset-password`: Đặt lại mật khẩu mới cho tài khoản.

