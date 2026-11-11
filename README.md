# CodeArena - Nền Tảng Chấm Bài Tự Động & Quản Trị Người Dùng (RBAC)

## Giới thiệu
Hệ thống website **CodeArena** (Đại học Công nghiệp Hà Nội - HaUI, Nhóm 14) được tích hợp trọn vẹn giữa:
- **Frontend**: Giao diện Sandbox IDE trực quan tích hợp **Cửa sổ Console / Terminal lập trình chuyên dụng** (xem trực tiếp stdout, stderr, mã thoát process, thời gian ms, bộ nhớ MB), Chấm điểm bài thi Giảng viên, Contest Arena (ICPC Leaderboard), Báo cáo Kết quả AI, và **Portal Quản lý Tài khoản (Admin)** được xây dựng bằng Tailwind CSS, responsive mượt mà, hỗ trợ phím tắt (`Ctrl + Enter` chạy thử, `Ctrl + Shift + Enter` nộp bài), tải/sao chép code, và phân quyền người dùng RBAC đa cấp.
- **Backend API**: Xây dựng bằng **FastAPI (Python 3.14)** sử dụng **Cơ sở dữ liệu SQLite** độc lập (`codearena.db` chạy ngay lập tức mà không cần cài đặt thêm bất kỳ phần mềm CSDL máy chủ nào), tích hợp engine thực thi mã nguồn Sandbox an toàn, thuật toán phát hiện đạo mã Winnowing AST, phân quyền RBAC đa cấp, và các API RESTful CRUD toàn diện.
- **Động cơ Đánh giá AI Kép (Dual AI Engine)**:
  1. **Google Gemini REST API (Online)**: Tích hợp trực tiếp mô hình `gemini-1.5-flash` qua Google REST API chuẩn mực (sử dụng thư viện chuẩn của Python, không phụ thuộc bên ngoài), phân tích độ phức tạp thời gian/bộ nhớ ($O(N)$, $O(N \log N)$), chất lượng Clean Code, và sinh nhận xét sư phạm chi tiết.
  2. **AST Static Heuristic Engine (Offline Fallback)**: Bộ phân tích cú pháp tĩnh AST tự động nhận diện độ sâu vòng lặp, đệ quy, tra cứu Hash Map, kiểm thử biên — hoạt động mượt mà ngay cả khi không có kết nối Internet hoặc chưa cấu hình API Key.

---

## Động cơ AI & Hướng dẫn Cấu hình Google Gemini

CodeArena tích hợp cơ chế thẩm định AI thực tế:
- **Kiểm tra trạng thái**: Nút badge `AI: ...` ở góc trên thanh Header cho phép theo dõi trực tiếp trạng thái của AI Engine (`Gemini 1.5 [Live]` hoặc `AST Engine [Local]`).
- **Cấu hình API Key linh hoạt qua 2 cách**:
  - **Cách 1 (Giao diện Web)**: Bấm trực tiếp vào nút `AI: ...` ở Header, dán API Key vào ô nhập liệu và bấm **Lưu & Kích hoạt**.
  - **Cách 2 (File môi trường)**: Thêm biến môi trường vào file `.env` hoặc hệ điều hành:
    ```bash
    GEMINI_API_KEY="AIzaSyYourGeminiApiKeyHere"
    GEMINI_MODEL="gemini-1.5-flash"
    ```
- **Lấy API Key miễn phí**: Nhận khóa API miễn phí từ [Google AI Studio](https://aistudio.google.com).
- **Cơ chế Fallback thông minh**: Khi chưa có API Key hoặc gặp sự cố mạng, hệ thống tự động kích hoạt **AST Static Heuristic Engine** để đảm bảo kỳ thi diễn ra liên tục, không bao giờ làm gián đoạn bài nộp của thí sinh.

---

## Cơ sở dữ liệu SQLite Thuần Túy & Tiện Lợi

Hệ thống sử dụng **SQLite** làm cơ sở dữ liệu duy nhất và chính thức:
- **Tự động khởi tạo**: File CSDL `codearena.db` được tự động tạo và cấu hình cấu trúc bảng ngay tại thư mục dự án khi khởi động máy chủ lần đầu.
- **Siêu nhẹ & Độc lập**: Không cần cài đặt máy chủ cơ sở dữ liệu bên ngoài, không cần cấu hình cổng mạng, không lo lỗi timeout kết nối.
- **Dữ liệu đầy đủ**: Tự động nạp sẵn 7 tài khoản mẫu ban đầu (Admin, Giảng viên, Sinh viên), ngân hàng bài tập và kỳ thi ICPC mẫu.

---

## Hướng dẫn khởi chạy

### Cách 1: Chạy nhanh bằng 1-Click trên Windows
Nhấp đúp chuột vào file:
```
start.bat
```
File này sẽ tự động kiểm tra Python, cài đặt thư viện cần thiết (`fastapi`, `uvicorn`, `pydantic`) và mở trình duyệt tại `http://localhost:8000`.

### Cách 2: Khởi chạy bằng dòng lệnh
```bash
# 1. Cài đặt thư viện
python -m pip install -r requirements.txt

# 2. Khởi chạy server FastAPI
python run_server.py
```

- **Website CodeArena**: [http://localhost:8000](http://localhost:8000)
- **Tài liệu Swagger API (Interactive Docs)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Tài liệu ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Kiểm tra trạng thái CSDL & Backend**: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- **Kiểm tra trạng thái Động cơ AI**: [http://localhost:8000/api/config/ai-status](http://localhost:8000/api/config/ai-status)

---

## Môi Trường Sandbox IDE & Console Terminal Lập Trình

Giao diện IDE được thiết kế chuẩn mực như các môi trường trực tuyến chuyên nghiệp:
- **Cửa sổ soạn thảo mã nguồn**: Hỗ trợ thụt lề bằng phím Tab (4 dấu cách), đổi đề bài, chuyển đổi ngôn ngữ Python 3 / C++, nạp code mẫu (AC/WA), nút **Reset** khôi phục mã nguồn ban đầu, và nút **Xóa code** (xóa trắng editor để làm lại từ đầu).
- **Phím tắt nhanh**:
  - `Ctrl + Enter`: Chạy thử mã nguồn (Run) và mở ngay **Console / Terminal**.
  - `Ctrl + Shift + Enter`: Nộp bài thi (Submit) vào hệ thống chấm tự động.
  - `Ctrl + S`: Lưu bài làm.
- **Cửa sổ 3 Sub-tab dưới Editor**:
  1. **Terminal / Console**: Cửa sổ giả lập terminal nền tối chuẩn lập trình. Hiển thị dòng lệnh `$ python3 -u solution.py`, chuẩn đầu ra `stdout` (màu xanh ngọc), thông báo ngoại lệ/lỗi cú pháp `stderr` (màu đỏ), Exit Code, thời gian chạy thực tế và bộ nhớ tiêu thụ. Tích hợp nút **Sao chép** và nút **Xóa console**.
  2. **Kết quả Chấm & AI**: Bảng đánh giá chi tiết test cases đã vượt qua, nhận xét giải thuật AI Rubric và phần trăm trùng lặp mã nguồn (AST Winnowing).
  3. **Test Case tùy chỉnh**: Cho phép nhập dữ liệu đầu vào thử nghiệm (`stdin`) tùy ý.

---

## Phân quyền chức năng theo Vai trò (RBAC System)

Hệ thống tự động ẩn/hiện và kiểm soát nghiêm ngặt quyền truy cập theo đúng vai trò tài khoản:
- **Học sinh**: Chỉ nhìn thấy và truy cập các chức năng của học sinh (Làm bài, nộp bài, thi đấu Contest, xem các bài thi của chính mình đã được Giảng viên chấm điểm).
- **Giáo viên**: Nhìn thấy các chức năng của giáo viên (Làm bài, Xem bài & Chấm điểm, Quản lý kỳ thi Contest, Báo cáo toàn lớp, Xóa bài làm, Rejudge). Hoàn toàn không nhìn thấy tab Quản lý Tài khoản của Admin.
- **Quản trị viên (Admin)**: Nhìn thấy tất cả mọi chức năng toàn hệ thống (bao gồm cả Cổng Quản lý Tài khoản độc quyền).

| Chức năng / Tab | Sinh viên | Giáo viên | Quản trị viên (Admin) | Khách (Chưa đăng nhập) |
| :--- | :---: | :---: | :---: | :---: |
| **Sandbox IDE** (Thực thi code) | Hiện | Hiện | Hiện | Hiện |
| **Nộp bài thi** (Submit) | **1 Lần duy nhất / bài** | Tự do kiểm thử | Tự do kiểm thử | Yêu cầu đăng nhập |
| **Contest Arena** (Leaderboard) | Hiện | Hiện | Hiện | Hiện |
| **Tạo / Hủy kỳ thi** (Contest Action) | **Ẩn** | **Hiện** | **Hiện** | **Ẩn** |
| **Kết quả & Nhận xét (`results`)** | **Xem bài ĐÃ ĐƯỢC CHẤM** | **HIỆN (Toàn lớp)** | **HIỆN (Toàn trường)** | **ẨN HOÀN TOÀN** |
| **Chấm AI / Rejudge / Rubric** | **Không có quyền** | **SỬ DỤNG TOÀN QUYỀN** | **SỬ DỤNG TOÀN QUYỀN** | **Không có quyền** |
| **Xem bài & Chấm điểm (`grading`)** | **ẨN HOÀN TOÀN** | **Hiện** | **Hiện** | **ẨN HOÀN TOÀN** |
| **Xóa bài làm của sinh viên** | **Không có quyền** | **Được phép xóa** | **Được phép xóa** | **Không có quyền** |
| **Quản lý Tài khoản (`accounts`)** | **ẨN HOÀN TOÀN** | **ẨN HOÀN TOÀN** | **HIỆN ĐỘC QUYỀN** | **ẨN HOÀN TOÀN** |

> [!IMPORTANT]
> **1. Quy chế Xem Điểm & Kết Quả của Học sinh / Sinh viên**:
> - Học sinh được phép truy cập tab **Kết quả & Nhận xét** để tra cứu **những bài làm đã được Giảng viên chấm điểm chính thức**.
> - Tại đây, học sinh xem được điểm số chính thức, lời phê / nhận xét của Giảng viên, các tiêu chí đánh giá AI Rubric, mã nguồn đã nộp và số test cases đã vượt qua.
> - Đối với bài làm **đang chờ chấm**, hệ thống hiển thị thông báo tiến độ chờ Giảng viên phê duyệt. Học sinh hoàn toàn không thể xem bài của bạn khác trong lớp.
>
> **2. Tách Biệt Nhiều Cổng Giao Diện (Multi-Portal Files)**:
> - **Cổng Tự Động Thích Ứng (Omni Portal)**: `http://localhost:8000/` (`index.html`) - Tự động nhận diện tài khoản đăng nhập để hiển thị chính xác các chức năng và quyền hạn được phép.
> - **Cổng Sinh Viên Chuyên Biệt**: `http://localhost:8000/student` (`student.html`) - Dành riêng cho Học sinh / Sinh viên (đã loại bỏ hoàn toàn các tab và mã nguồn Chấm bài và Quản lý tài khoản).
> - **Cổng Giảng Viên Chuyên Biệt**: `http://localhost:8000/teacher` (`teacher.html`) - Dành riêng cho Giảng viên (chấm bài, rejudge, xóa bài thi, quản lý kỳ thi).
> - **Cổng Quản Trị Viên Chuyên Biệt**: `http://localhost:8000/admin` (`admin.html`) - Toàn quyền quản trị tài khoản và hệ thống.
>
> **3. Quy chế Nộp bài 1 Lần Duy Nhất**:
> - Mỗi học sinh chỉ được phép nộp bài **1 lần duy nhất cho mỗi bài tập**. Sau khi đã nộp, nút nộp bài sẽ chuyển sang trạng thái đã nộp và khóa lại để giữ kỷ luật phòng thi.
> - Giảng viên và Quản trị viên (Admin) được nộp bài tự do để kiểm thử hệ thống.

---

## Danh sách tài khoản mẫu mặc định

| Vai trò (Role) | Họ và tên | Email | Mật khẩu | Mã ID | Quyền hạn & Chức năng hiển thị |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Admin (Quản trị viên)** | Quản trị viên Hệ thống | `admin@haui.edu.vn` | `admin` | `ADMIN-01` | Toàn quyền Thêm, Sửa, Xóa, Khóa tài khoản, cấu hình AI, xem và truy cập tất cả các tab |
| **Giáo viên** | TS. Nguyễn Thị Hoa Huệ | `gv.huenth@haui.edu.vn` | `password123` | `GV-HAUI-01` | Chấm điểm bài thi, sử dụng AI Rubric, tạo/hủy kỳ thi, quản lý bài tập, xem báo cáo toàn lớp (Ẩn tab Quản lý Tài khoản) |
| **Sinh viên** | Hoàng Anh Tú | `20240606239@sv.haui.edu.vn` | `password123` | `20240606239` | Luyện tập Sandbox IDE, tham gia Contest, xem bảng điểm cá nhân (Ẩn tab Chấm điểm và Quản lý Tài khoản) |
| **Sinh viên** | Nguyễn Kim Huy | `20240606240@sv.haui.edu.vn` | `password123` | `20240606240` | Sinh viên thành viên |
| **Sinh viên** | Nguyễn Cảnh Hải | `20240606241@sv.haui.edu.vn` | `password123` | `20240606241` | Sinh viên thành viên |
| **Sinh viên** | Lưu Quang Huy | `20240606242@sv.haui.edu.vn` | `password123` | `20240606242` | Sinh viên thành viên |
| **Sinh viên** | Hoàng Thái Hưng | `20240606243@sv.haui.edu.vn` | `password123` | `20240606243` | Sinh viên thành viên |

*(Lưu ý: Bạn có thể bấm nút **1-Click Test** trong cửa sổ Đăng nhập để chuyển đổi giữa các vai trò ngay lập tức hoặc bấm nút **Đăng xuất** ở Header để thử nghiệm quyền Khách)*

---

## Cấu trúc thư mục

```
d:\Arenacode\
├── backend/
│   ├── __init__.py
│   ├── auth.py             # Băm mật khẩu PBKDF2-HMAC-SHA256, xác thực bảo mật, tạo avatar
│   ├── config.py           # Quản lý cấu hình SQLite, Google Gemini API Key, port máy chủ
│   ├── database.py         # Module CSDL SQLite độc lập, khởi tạo bảng, CRUD users/submissions/contests
│   ├── judge.py            # Sandbox Engine thực thi Python cô lập, Google Gemini REST API & Winnowing AST
│   ├── models.py           # Pydantic schemas (User, Submission, Contest, Judge, Auth, Stats, AIConfig)
│   ├── problems.py         # Định nghĩa ngân hàng bài tập (CA-101 đến CA-104), test cases, lời giải mẫu
│   ├── create_portals.py   # Script tạo các cổng chuyên biệt (student.html, teacher.html, admin.html)
│   └── main.py             # FastAPI app, CORS middleware, 30 RESTful endpoints và phục vụ Frontend
├── codearena.db            # Cơ sở dữ liệu SQLite chính thức
├── .env.example            # Mẫu file cấu hình môi trường cho server
├── index.html              # Toàn bộ giao diện Frontend CodeArena (Omni Portal)
├── student.html            # Cổng giao diện chuyên biệt cho Sinh viên
├── teacher.html            # Cổng giao diện chuyên biệt cho Giảng viên
├── admin.html              # Cổng giao diện chuyên biệt cho Quản trị viên
├── requirements.txt        # Danh sách thư viện Python siêu gọn (fastapi, uvicorn, pydantic)
├── run_server.py           # Script chạy máy chủ FastAPI (Port 8000)
└── start.bat               # Script khởi động 1-click cho Windows
```

---

## Danh sách RESTful API Endpoints

### 1. Xác thực & Thống kê
- `GET /api/health`: Kiểm tra trạng thái máy chủ, phiên bản, thông tin CSDL SQLite và Sandbox engine.
- `GET /api/stats`: Thống kê tổng quan số lượng tài khoản (Admin, Giáo viên, Sinh viên, Trạng thái).
- `POST /api/auth/login`: Đăng nhập bằng Email và Mật khẩu (kiểm tra tài khoản khóa, cấp session token).

### 2. Cấu hình & Trạng thái AI
- `GET /api/config/ai-status`: Kiểm tra trạng thái hoạt động của AI Engine (Gemini 1.5 Flash hoặc AST Static Analyzer).
- `POST /api/config/gemini-key`: Cập nhật Google Gemini API Key trực tiếp từ giao diện Quản trị / Giảng viên.

### 3. Sandbox Online Judge & Chấm Điểm AI
- `POST /api/judge/run`: Chạy thử mã nguồn trên Sandbox cô lập với timeout 3s, thu thập stdout/stderr, runtime (ms) và bộ nhớ (MB).
- `POST /api/judge/submit`: Nộp bài chấm điểm tự động qua bộ test cases, phân tích AI đánh giá giải thuật, quét độ trùng lặp AST (Winnowing) và lưu vào SQLite (Quy chế: Mỗi học sinh chỉ được nộp bài 1 lần duy nhất cho mỗi bài).

### 4. Quản lý Bài nộp & Chấm điểm Giảng viên
- `GET /api/submissions`: Lấy danh sách bài nộp (hỗ trợ lọc theo `student_id`, `problem_id`, `status`, tìm kiếm `q`).
- `GET /api/submissions/{sub_id}`: Xem chi tiết một bài nộp, mã nguồn và báo cáo rubric.
- `PUT /api/submissions/{sub_id}/grade`: Giảng viên chấm điểm chính thức, ghi nhận xét và công bố kết quả.
- `DELETE /api/submissions/{sub_id}`: Xóa vĩnh viễn bài làm của sinh viên khỏi CSDL SQLite (cho phép sinh viên nộp lại bài mới khi có sự cố).
- `POST /api/submissions/{sub_id}/rejudge`: Kích hoạt Sandbox & AI chấm lại bài nộp.
- `POST /api/submissions/batch-rejudge`: Chấm lại toàn bộ bài nộp của lớp.

### 5. Quản lý Kỳ thi (Contest Arena)
- `GET /api/contests`: Lấy danh sách các kỳ thi đang diễn ra và lịch sử kỳ thi.
- `GET /api/contests/{contest_id}`: Xem chi tiết kỳ thi.
- `POST /api/contests`: Giảng viên tạo kỳ thi mới với danh sách bài tập tùy chọn.
- `POST /api/contests/{contest_id}/cancel`: Hủy kỳ thi và đóng băng bảng điểm.

### 6. Ngân hàng Đề thi
- `GET /api/problems`: Lấy toàn bộ danh sách bài tập, mô tả, ràng buộc và test cases mẫu.
- `GET /api/problems/{problem_id}`: Xem thông tin chi tiết một bài tập.

### 7. Quản lý Tài khoản (Admin CRUD)
- `GET /api/users`: Lấy danh sách người dùng (tìm kiếm `q`, lọc theo `role`, `status`).
- `GET /api/users/{user_id}`: Xem chi tiết một tài khoản.
- `POST /api/users`: Tạo mới tài khoản (kiểm tra trùng mã ID, email, mã hóa mật khẩu).
- `PUT /api/users/{user_id}`: Cập nhật thông tin tài khoản hoặc đổi mật khẩu.
- `DELETE /api/users/{user_id}`: Xóa tài khoản (bảo vệ tài khoản gốc `ADMIN-01`).
- `POST /api/users/{user_id}/toggle-status`: Bật/tắt trạng thái Khóa (`locked`) hoặc Hoạt động (`active`).
- `POST /api/users/{user_id}/reset-password`: Đặt lại mật khẩu mới cho tài khoản.
