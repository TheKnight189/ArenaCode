# CodeArena - Nền Tảng Luyện Tập Lập Trình Trực Tuyến & Chấm Bài Tự Động Sandbox

> **Đại học Công nghiệp Hà Nội (HaUI) - Khoa Công nghệ Thông tin**  
> **Đề tài Bài tập lớn**: Xây dựng nền tảng luyện tập lập trình trực tuyến CodeArena: chấm bài tự động trong môi trường sandbox, phân tích giải thuật AI và phát hiện gian lận sao chép mã nguồn.  
> **Thành viên thực hiện (Nhóm 14)**:
> - Hoàng Anh Tú - `20240606239`
> - Nguyễn Kim Huy - `20240606240`
> - Nguyễn Cảnh Hải - `20240606241`
> - Lưu Quang Huy - `20240606242`
> - Hoàng Thái Hưng - `20240606243`

---

## Mục lục
1. [Giới thiệu Hệ thống](#giới-thiệu-hệ-thống)
2. [Kiến trúc & Tính năng Nổi bật](#kiến-trúc--tính-năng-nổi-bật)
3. [Động cơ Chấm Sandbox & An toàn Thực thi](#động-cơ-chấm-sandbox--an-toàn-thực-thi)
4. [Động cơ AI Kép (Dual AI Engine)](#động-cơ-ai-kép-dual-ai-engine)
5. [Hàng đợi Redis & Async Worker Pool](#hàng-đợi-redis--async-worker-pool)
6. [Hệ thống Phát hiện Gian lận (Anti-Cheat AST Winnowing)](#hệ-thống-phát-hiện-gian-lận-anti-cheat-ast-winnowing)
7. [Quản lý Đề thi & Test Case Ẩn / Hiện](#quản-lý-đề-thi--test-case-ẩn--hiện)
8. [Thống kê theo Chủ đề & Nhật ký Hệ thống (Audit Logs)](#thống-kê-theo-chủ-đề--nhật-ký-hệ-thống-audit-logs)
9. [Cơ sở dữ liệu Kép (PostgreSQL Cloud & SQLite Local)](#cơ-sở-dữ-liệu-kép-postgresql-cloud--sqlite-local)
10. [Phân quyền Người dùng (RBAC) & Cổng Portal Riêng biệt](#phân-quyền-người-dùng-rbac--cổng-portal-riêng-biệt)
11. [Danh sách Tài khoản Mẫu](#danh-sách-tài-khoản-mẫu)
12. [Hướng dẫn Cài đặt & Khởi chạy](#hướng-dẫn-cài-đặt--khởi-chạy)
13. [Hướng dẫn Triển khai Cloud (Render / Neon / Supabase)](#hướng-dẫn-triển-khai-cloud-render--neon--supabase)
14. [Danh mục RESTful API Endpoints](#danh-mục-restful-api-endpoints)
15. [Cấu trúc Thư mục Dự án](#cấu-trúc-thư-mục-dự-án)

---

## Giới thiệu Hệ thống

**CodeArena** là nền tảng Online Judge toàn diện được thiết kế chuyên biệt phục vụ công tác giảng dạy, luyện tập lập trình thuật toán và thi đấu trực tuyến tại các trường đại học:
- **Giao diện Sharp Geometric IDE**: Phong cách thiết kế kỹ thuật hiện đại, các hộp và thẻ góc vuông dứt khoát (`border-radius: 0px` / `rounded-none`), kết hợp bảng điều khiển mô phỏng Terminal lập trình chuẩn mực (`stdout`, `stderr`, runtime ms, memory MB, Exit Code).
- **Hệ thống chấm tự động đa lớp (Multi-layer Sandbox)**: Đảm bảo kiểm soát tuyệt đối về tài nguyên CPU, bộ nhớ RAM (256MB), thời gian chạy (3s) và cách ly mạng, bảo vệ an toàn máy chủ trước các nguy cơ tấn công qua mã nguồn thí sinh.
- **Phân định rõ ràng lỗi biên dịch (CE) và lỗi thực thi (RTE)**: Kiểm tra cú pháp trước khi chạy, trả về thông báo lỗi chuẩn xác theo quy chuẩn chấm thi quốc tế (ICPC / ACM).
- **Phát hiện gian lận sao chép mã nguồn (Plagiarism Detection)**: Sử dụng thuật toán **Winnowing** trên cây cú pháp trừu tượng **AST**, chống lại các hành vi lách luật như đổi tên biến, tái cấu trúc hàm hay xáo trộn thứ tự câu lệnh.
- **Trợ lý Sư phạm AI Kép**: Tích hợp trực tiếp **Google Gemini 1.5 Flash API** và bộ giải thích tĩnh **AST Heuristic Engine**, tự động sinh nhận xét thuật toán, ước tính độ phức tạp thời gian/không gian ($O(N)$, $O(N \log N)$) và Clean Code.

---

## Kiến trúc & Tính năng Nổi bật

| Thành phần | Công nghệ chính | Chức năng nổi bật |
| :--- | :--- | :--- |
| **Frontend** | Tailwind CSS, Vanilla JS (ES6+), Monaco/Ace-like Editor | Thiết kế góc vuông sắc nét, phím tắt nhanh (`Ctrl + Enter` chạy code, `Ctrl + Shift + Enter` nộp bài, `Ctrl + S`), Terminal đa luồng, thông báo chuông & pop-up thời gian thực. |
| **Backend API** | FastAPI (Python 3.10+ / 3.14), Uvicorn ASGI Server | Hơn 40 RESTful endpoints, tài liệu Swagger UI tương tác trực tiếp (`/docs`), kiến trúc mở rộng theo module. |
| **Sandbox Execution** | Docker Engine API, Windows Job Objects / Linux `resource`, Subprocess Jail | Giới hạn 256MB RAM, timeout 3s, cô lập network socket, phân định Compile Error (CE) vs Runtime Error (RTE). |
| **Hàng đợi Xử lý** | Redis Queue, Async Background Worker Pool | Hỗ trợ xếp hàng xử lý hàng trăm bài nộp đồng thời, tự động cân bằng tải và giám sát tiến độ theo thời gian thực. |
| **Cơ sở dữ liệu** | SQLite 3 (`codearena.db`) & PostgreSQL (Cloud) | Tự động chuyển đổi mượt mà giữa CSDL đám mây (Render, Supabase, Neon) và SQLite nội bộ. |
| **Bảo mật & RBAC** | PBKDF2-HMAC-SHA256, Session Token, Multi-Portals | Phân quyền 4 cấp (Sinh viên, Giảng viên, Admin, Khách), 4 tệp giao diện độc lập bảo mật phía client. |

---

## Động cơ Chấm Sandbox & An toàn Thực thi

Hệ thống cung cấp cơ chế bảo vệ máy chủ đa tầng khi thực thi mã nguồn của thí sinh:

```
[Mã nguồn nộp] 
       │
       ▼
 [Kiểm tra Cú pháp AST / py_compile] ──(Lỗi cú pháp)──► Compile Error (CE)
       │ (Hợp lệ)
       ▼
 [Phân phối Hàng đợi Worker] 
       │
       ├──► Chế độ 1: Docker Sandbox Container
       │      ├── RAM Hard Limit: 256MB (--memory=256m)
       │      ├── CPU Cores: 1.0 Core (--cpus=1.0)
       │      ├── Network Mode: Cách ly hoàn toàn (--network none)
       │      └── Timeout: 3.0 giây
       │
       └──► Chế độ 2: Process Jail (Windows Job Object / Linux setrlimit)
              ├── Chặn hoàn toàn socket/HTTP/urllib
              ├── Giới hạn 256MB RAM tiến trình
              └── Timeout 3.0 giây (Subprocess Watchdog)
```

- **Phân biệt Compile Error (CE) vs Runtime Error (RTE)**:
  - Nếu mã nguồn gặp lỗi cú pháp (`SyntaxError`, `IndentationError`, `TabError`), hệ thống bắt giữ ngay tại bước phân tích cú pháp AST trước khi khởi chạy tiến trình và trả về **Compile Error (CE)** kèm số dòng và gợi ý sửa chữa.
  - Nếu mã nguồn hợp lệ về mặt cú pháp nhưng gặp lỗi trong quá trình thực thi (`ZeroDivisionError`, `IndexError`, `KeyError`, `RecursionError`), hệ thống ghi nhận là **Runtime Error (RTE)**.
  - Nếu vượt quá thời gian cho phép: **Time Limit Exceeded (TLE)**.
  - Nếu vượt quá bộ nhớ: **Memory Limit Exceeded (MLE)**.
- **Bảng điều khiển Cấu hình Tài nguyên Động (Resource Sandbox Modal)**:
  - Giảng viên và Quản trị viên có thể mở modal cấu hình trực tiếp trên thanh công cụ để tinh chỉnh:
    - Mức RAM trần (64MB - 1024MB).
    - Thời gian chạy tối đa (1s - 15s).
    - Số lượng tiến trình worker xử lý song song (1 - 16 workers).
    - Công tắc kích hoạt / vô hiệu hóa Chặn kết nối mạng Socket.

---

## Động cơ AI Kép (Dual AI Engine)

CodeArena triển khai kiến trúc thẩm định trí tuệ nhân tạo dự phòng 2 tầng:

1. **Google Gemini 1.5 Flash (Online REST API)**:
   - Kết nối trực tiếp qua Google Generative AI REST API chuẩn của Python (không phụ thuộc SDK cồng kềnh).
   - Đánh giá chất lượng mã nguồn theo 4 tiêu chí chuẩn sư phạm (Rubric):
     - **Tính tối ưu thuật toán & Độ phức tạp thời gian/không gian** (ước lượng $O(N)$, $O(N \log N)$, $O(N^2)$).
     - **Chất lượng cấu trúc & Clean Code** (cách đặt tên biến, phân chia hàm, tuân thủ PEP8).
     - **Xử lý ca biên (Edge Cases)** (mảng rỗng, giá trị âm, tràn số nguyên).
     - **Nhận xét tổng thể & Gợi ý cải tiến** (giải pháp nâng cao để tối ưu điểm số).
2. **AST Static Heuristic Engine (Offline Fallback)**:
   - Được kích hoạt tự động khi không có kết nối Internet, chưa cấu hình API Key, hoặc dịch vụ ngoài gặp sự cố.
   - Phân tích trực tiếp cây cú pháp trừu tượng (Abstract Syntax Tree) của Python: đo độ sâu vòng lặp lồng nhau, kiểm tra đệ quy, tra cứu bảng băm (`dict`/`set`), nhận diện mẫu thiết kế thuật toán.
   - Đảm bảo 100% các kỳ thi diễn ra liên tục, không bao giờ bị gián đoạn hay treo tiến trình chấm.

---

## Hàng đợi Redis & Async Worker Pool

Nhằm giải quyết triệt để vấn đề quá tải khi hàng trăm sinh viên cùng nộp bài trong các kỳ thi chung:
- **Redis Queue**: Hỗ trợ kết nối Redis máy chủ qua biến môi trường `REDIS_URL` (hỗ trợ Redis Cloud, Upstash, hoặc Redis Container).
- **Worker Pool Đa luồng**: Nhóm tiến trình worker chạy nền liên tục lấy các bài nộp từ hàng đợi, chuyển vào Sandbox để biên dịch, thực thi từng test case và ghi nhận kết quả vào CSDL.
- **Giám sát Trạng thái Thời gian thực**: Giao diện hiển thị trực quan thông tin hàng đợi: số lượng bài đang chờ (`Pending`), số bài đang xử lý (`Processing`), số worker hoạt động và độ trễ trung bình.

---

## Hệ thống Phát hiện Gian lận (Anti-Cheat AST Winnowing)

Hệ thống tích hợp thuật toán phân tích độ tương đồng nâng cao:
- **Chuẩn hóa cây cú pháp AST**: Loại bỏ hoàn toàn sự can thiệp của việc đổi tên biến, thay đổi tên hàm, thêm/bớt khoảng trắng, hoặc hoán đổi vị trí các dòng lệnh độc lập.
- **Thuật toán Fingerprinting Winnowing**: Băm các k-gram của cây cú pháp và trích xuất footprint tiêu biểu của bài nộp, so sánh chéo từng cặp bài nộp trong cùng một kỳ thi.
- **Thanh trượt Ngưỡng cảnh báo Hiệu chuẩn Chuẩn xác**:
  - **Dưới 65% (Chặt chẽ / Nghiêm ngặt)**: Bắt cả những đoạn giải thuật ngắn tương đồng hoặc cấu trúc hàm tương tự.
  - **65% - 85% (Chuẩn - Khuyên dùng)**: Phát hiện sao chép giải thuật cốt lõi có chỉnh sửa tên biến.
  - **Trên 85% (Nới lỏng)**: Chỉ cảnh báo khi bài thi là bản sao chép y hệt (gần như 100% giống nhau).
- **Giao diện So sánh Trực quan (Diff Inspector)**: Bôi màu nổi bật các đoạn code nghi vấn giữa 2 bài nộp cạnh nhau để Giảng viên đưa ra quyết định công tâm nhất.

---

## Quản lý Đề thi & Test Case Ẩn / Hiện

Hệ thống cho phép Giảng viên và Quản trị viên toàn quyền quản lý ngân hàng câu hỏi bền vững:
- **Lưu trữ CSDL Vĩnh viễn**: Mọi thao tác thêm đề bài mới, chỉnh sửa đề bài và xóa đề bài đều được lưu trực tiếp vào bảng `problems` (SQLite / PostgreSQL), không bị mất khi khởi động lại server.
- **Phân loại Test Case Ẩn (Hidden) và Test Case Mẫu (Visible)**:
  - **Test Case Mẫu (Visible)**: Hiển thị công khai trong phần mô tả bài toán, giúp sinh viên hiểu rõ định dạng Input/Output và chạy thử nghiệm trong Sandbox.
  - **Test Case Ẩn (Hidden)**: Được bảo mật tuyệt đối, chỉ hệ thống chấm điểm mới có quyền truy cập khi thí sinh nộp bài. Ngăn chặn triệt để hành vi sinh viên "hardcode" kết quả dạng `if input == ...: print(...)`.
- **Hỗ trợ Code Mẫu Kép**: Lưu trữ cả lời giải chuẩn (AC Solution) và mã nguồn thử nghiệm có lỗi (Buggy Solution) bằng cả Python và C++ phục vụ kiểm thử bài toán.

---

## Thống kê theo Chủ đề & Nhật ký Hệ thống (Audit Logs)

### 1. Thống kê theo Chủ đề Thuật toán (Topic Statistics Analytics)
Tab **Thống kê Chủ đề** cung cấp cái nhìn trực quan và toàn diện về tiến độ học tập:
- Phân nhóm bài tập theo các chuyên đề thuật toán: *Mảng & Mảng hai chiều (Array)*, *Bảng băm (Hash Map)*, *Quy hoạch động (Dynamic Programming)*, *Kỹ thuật Hai con trỏ (Two Pointers)*, *Xử lý Chuỗi (String)*, *Toán học & Số học (Math)*, *Đồ thị (Graph)*.
- Thống kê tỷ lệ đạt (% AC), tổng lượt nộp, số bài tập mỗi chuyên đề.
- Bảng vàng vinh danh **Top 3 Sinh viên dẫn đầu** theo từng chủ đề.

### 2. Màn hình Nhật ký Hệ thống (System Audit Logs)
Phục vụ quản trị và liêm chính học thuật:
- Ghi nhận chi tiết từng sự kiện: Đăng nhập/Đăng xuất, Nộp bài, Thay đổi cấu hình Sandbox, Giảng viên chấm điểm, Tạo/Hủy kỳ thi, Xóa bài làm.
- Phân loại mức độ sự kiện với màu sắc trực quan: `INFO` (Xanh lục), `WARNING` (Hổ phách), `ERROR` (Đỏ hồng).
- Tìm kiếm theo từ khóa, lọc theo module, xóa log định kỳ và **Xuất toàn bộ nhật ký ra file JSON (Export Logs)**.

---

## Cơ sở dữ liệu Kép (PostgreSQL Cloud & SQLite Local)

CodeArena tích hợp khả năng nhận diện CSDL thông minh:
- **Khi chạy trên Đám mây (Cloud)**:
  - Chỉ cần khai báo biến môi trường `DATABASE_URL` trỏ tới PostgreSQL (Render PostgreSQL, Supabase, Neon).
  - Hệ thống tự động thiết lập kết nối `psycopg2`, tạo đầy đủ các bảng (`users`, `submissions`, `contests`, `problems`, `system_logs`) và tự động nạp dữ liệu mẫu ban đầu (`seed_data`).
- **Khi chạy Cục bộ (Local Machine)**:
  - Tự động fallback về file CSDL **SQLite** độc lập `codearena.db`. Không cần cài đặt bất kỳ dịch vụ máy chủ CSDL nào bên ngoài, khởi chạy ngay lập tức chỉ với 1 lệnh.

---

## Phân quyền Người dùng (RBAC) & Cổng Portal Riêng biệt

Hệ thống áp dụng cơ chế kiểm soát truy cập dựa trên vai trò (Role-Based Access Control):

| Chức năng / Quyền hạn | Sinh viên | Giáo viên | Quản trị viên (Admin) | Khách (Chưa đăng nhập) |
| :--- | :---: | :---: | :---: | :---: |
| **Sandbox IDE** (Thực thi code) | Có | Có | Có | Có |
| **Nộp bài thi** (Submit) | **1 Lần duy nhất / bài** | Tự do kiểm thử | Tự do kiểm thử | Yêu cầu đăng nhập |
| **Contest Arena** (Leaderboard) | Có | Có | Có | Có |
| **Tạo / Hủy kỳ thi** | Không | **Có quyền** | **Có quyền** | Không |
| **Thêm / Sửa / Xóa Đề bài** | Không | **Có quyền** | **Có quyền** | Không |
| **Xem Kết quả & Nhận xét AI** | **Chỉ bài ĐÃ CHẤM** | **Toàn lớp** | **Toàn hệ thống** | Không |
| **Chấm điểm / Phúc khảo / Rejudge** | Không | **Có quyền** | **Có quyền** | Không |
| **Cấu hình Sandbox & Hàng đợi** | Không | **Có quyền** | **Có quyền** | Không |
| **Thống kê Chủ đề & Nhật ký Logs** | Không | **Có quyền** | **Có quyền** | Không |
| **Quản lý Tài khoản (Thêm/Sửa/Xóa)** | Không | Không | **TOÀN QUYỀN ĐỘC QUYỀN** | Không |

### 4 Cổng Giao diện Độc lập (Multi-Portals)
Để tăng cường bảo mật và tách bạch không gian làm việc, hệ thống cung cấp 4 tệp giao diện:
1. **Cổng Tự Động (Omni Portal)**: [index.html](file:///d:/Arenacode/index.html) (`/`) - Tự động thích ứng giao diện dựa trên vai trò tài khoản đăng nhập.
2. **Cổng Sinh Viên (Student Portal)**: [student.html](file:///d:/Arenacode/student.html) (`/student`) - Loại bỏ hoàn toàn mã nguồn và các modal của Giảng viên/Admin khỏi DOM.
3. **Cổng Giảng Viên (Teacher Portal)**: [teacher.html](file:///d:/Arenacode/teacher.html) (`/teacher`) - Đầy đủ tính năng chấm bài, quản lý bài tập, ngân hàng test case, nhưng loại bỏ hoàn toàn tab Quản trị tài khoản.
4. **Cổng Quản Trị Viên (Admin Portal)**: [admin.html](file:///d:/Arenacode/admin.html) (`/admin`) - Toàn quyền quản trị tài khoản người dùng và hệ thống.

---

## Danh sách Tài khoản Mẫu

| Vai trò | Họ và tên | Email | Mật khẩu mặc định | Mã định danh | Mô tả quyền hạn |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Admin** | Quản trị viên Hệ thống | `admin@haui.edu.vn` | `admin` | `ADMIN-01` | Toàn quyền thêm, sửa, xóa, khóa tài khoản, cấu hình AI, quản trị logs |
| **Giáo viên** | TS. Nguyễn Thị Hoa Huệ | `gv.huenth@haui.edu.vn` | `password123` | `GV-HAUI-01` | Quản lý đề bài, test cases ẩn, chấm điểm rubric, cấu hình sandbox |
| **Sinh viên** | Hoàng Anh Tú | `20240606239@sv.haui.edu.vn` | `password123` | `20240606239` | Làm bài Sandbox IDE, thi đấu Contest, xem bài thi đã được chấm |
| **Sinh viên** | Nguyễn Kim Huy | `20240606240@sv.haui.edu.vn` | `password123` | `20240606240` | Sinh viên thành viên |
| **Sinh viên** | Nguyễn Cảnh Hải | `20240606241@sv.haui.edu.vn` | `password123` | `20240606241` | Sinh viên thành viên |
| **Sinh viên** | Lưu Quang Huy | `20240606242@sv.haui.edu.vn` | `password123` | `20240606242` | Sinh viên thành viên |
| **Sinh viên** | Hoàng Thái Hưng | `20240606243@sv.haui.edu.vn` | `password123` | `20240606243` | Sinh viên thành viên |

*(Ghi chú: Tại màn hình Đăng nhập có sẵn các nút **1-Click Test** để chuyển đổi nhanh giữa các vai trò khi chấm bài thử nghiệm).*

---

## Hướng dẫn Cài đặt & Khởi chạy

### Yêu cầu Môi trường
- Python 3.10 trở lên (khuyên dùng Python 3.11 - 3.14).
- Trình duyệt web hiện đại (Google Chrome, Microsoft Edge, Firefox, Brave).

### Cách 1: Khởi động Nhanh 1-Click trên Windows
Nhấp đúp chuột vào file:
```cmd
start.bat
```
Script sẽ tự động kiểm tra môi trường Python, cài đặt các gói cần thiết và mở trình duyệt web tại `http://localhost:8000`.

### Cách 2: Khởi động bằng Dòng lệnh (Terminal / PowerShell)
```bash
# 1. Di chuyển vào thư mục dự án
cd d:\Arenacode

# 2. Cài đặt các thư viện cần thiết
python -m pip install -r requirements.txt

# 3. Khởi chạy máy chủ FastAPI
python run_server.py
```

Sau khi máy chủ khởi động thành công:
- **Giao diện Web CodeArena**: [http://localhost:8000](http://localhost:8000)
- **Tài liệu Swagger API tương tác**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Tài liệu ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Kiểm tra sức khỏe Backend & CSDL**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## Hướng dẫn Triển khai Cloud (Render / Neon / Supabase)

Dự án đã được tích hợp sẵn đầy đủ cấu hình phục vụ việc triển khai lên các nền tảng đám mây:

### 1. File cấu hình có sẵn
- `render.yaml`: Blueprint cấu hình Web Service + PostgreSQL Database tự động trên Render.
- `Dockerfile`: Môi trường container hóa chạy Python 3.11, cài đặt sẵn GCC/G++ cho C++ và Docker CLI.
- `Procfile`: Định nghĩa lệnh chạy cho nền tảng PaaS: `web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.

### 2. Các Biến Môi Trường (Environment Variables)
Khi triển khai lên Render hoặc máy chủ VPS, cấu hình các biến môi trường sau:
```bash
# CSDL PostgreSQL (Render PostgreSQL / Neon / Supabase)
DATABASE_URL=postgres://user:password@hostname:5432/dbname

# Hàng đợi Redis (Tùy chọn)
REDIS_URL=rediss://default:password@hostname:6379

# Google Gemini API Key (Tùy chọn - có thể cấu hình trực tiếp trên Web)
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere
GEMINI_MODEL=gemini-1.5-flash

# Giới hạn Sandbox mặc định
SANDBOX_MEMORY_MB=256
SANDBOX_TIMEOUT_SEC=3.0
SANDBOX_NET_BLOCK=true
QUEUE_WORKERS=4
```

---

## Danh mục RESTful API Endpoints

Hệ thống cung cấp hơn 40 API chuẩn mực:

### 1. Trạng thái & Kiểm tra Sức khỏe (Health & Sandbox)
- `GET /api/health`: Kiểm tra trạng thái máy chủ, CSDL đang kết nối (SQLite/PostgreSQL) và bộ nhớ.
- `GET /api/sandbox/status`: Báo cáo chi tiết trạng thái Sandbox (Docker/Process Jail, RAM, Timeout, Chặn mạng).
- `GET /api/sandbox/config`: Lấy cấu hình tài nguyên Sandbox hiện tại.
- `PUT /api/sandbox/config`: Cập nhật cấu hình tài nguyên Sandbox (RAM, Timeout, Workers, NetBlock).
- `GET /api/queue/stats`: Lấy thống kê hàng đợi Redis & Worker pool thời gian thực.
- `POST /api/queue/test-redis`: Kiểm tra kết nối tới đường dẫn Redis URL.

### 2. Xác thực & Tài khoản (Auth & RBAC)
- `POST /api/auth/login`: Xác thực đăng nhập qua Email/Password, cấp session token.
- `GET /api/users`: Lấy danh sách tài khoản (hỗ trợ lọc `role`, `status`, tìm kiếm `q`).
- `GET /api/users/{user_id}`: Xem chi tiết tài khoản.
- `POST /api/users`: Tạo tài khoản mới (mã hóa mật khẩu PBKDF2).
- `PUT /api/users/{user_id}`: Cập nhật thông tin tài khoản hoặc đổi mật khẩu.
- `DELETE /api/users/{user_id}`: Xóa tài khoản (bảo vệ tài khoản gốc `ADMIN-01`).
- `POST /api/users/{user_id}/toggle-status`: Khóa hoặc kích hoạt lại tài khoản.
- `POST /api/users/{user_id}/reset-password`: Đặt lại mật khẩu về mặc định.

### 3. Động cơ AI & Cấu hình
- `GET /api/config/ai-status`: Kiểm tra trạng thái mô hình AI (Gemini Live hay AST Local).
- `POST /api/config/gemini-key`: Cập nhật và kích hoạt Google Gemini API Key.

### 4. Online Judge & Chấm bài Tự động
- `POST /api/judge/run`: Chạy thử mã nguồn trong Sandbox (nhận `stdout`, `stderr`, runtime, memory).
- `POST /api/judge/submit`: Nộp bài chấm chính thức (kiểm tra test case ẩn/hiện, phân tích AI Rubric, kiểm tra trùng lặp AST Winnowing, lưu vào CSDL).

### 5. Quản lý Bài nộp (Submissions)
- `GET /api/submissions`: Lấy danh sách bài nộp của lớp hoặc trường.
- `GET /api/submissions/{sub_id}`: Xem chi tiết bài nộp, mã nguồn và nhận xét.
- `PUT /api/submissions/{sub_id}/grade`: Giảng viên chấm điểm chính thức và công bố kết quả.
- `DELETE /api/submissions/{sub_id}`: Xóa vĩnh viễn bài làm của sinh viên khỏi CSDL.
- `POST /api/submissions/{sub_id}/rejudge`: Yêu cầu Sandbox và AI chấm lại 1 bài nộp.
- `POST /api/submissions/batch-rejudge`: Chấm lại toàn bộ bài nộp của cả lớp.

### 6. Quản lý Ngân hàng Đề bài (Problems CRUD)
- `GET /api/problems`: Lấy danh sách toàn bộ bài tập và test case mẫu.
- `GET /api/problems/{problem_id}`: Lấy chi tiết đề bài và bộ test case đầy đủ.
- `POST /api/problems`: Tạo đề bài mới kèm bộ test case ẩn/hiện và lưu vĩnh viễn vào CSDL.
- `PUT /api/problems/{problem_id}`: Cập nhật nội dung đề bài, thời gian, bộ nhớ và test cases.
- `DELETE /api/problems/{problem_id}`: Xóa vĩnh viễn đề bài khỏi ngân hàng đề thi.

### 7. Quản lý Kỳ thi (Contest Arena)
- `GET /api/contests`: Danh sách kỳ thi đang diễn ra và lịch sử.
- `GET /api/contests/{contest_id}`: Chi tiết kỳ thi và bảng điểm ICPC.
- `POST /api/contests`: Giảng viên tạo kỳ thi mới.
- `POST /api/contests/{contest_id}/cancel`: Hủy kỳ thi và đóng băng kết quả.

### 8. Thống kê Chuyên đề & Nhật ký Hệ thống (Audit Logs)
- `GET /api/stats`: Thống kê tổng quan số lượng tài khoản theo vai trò.
- `GET /api/stats/topics`: Thống kê chuyên sâu tỷ lệ đạt và bảng vàng top sinh viên theo từng chủ đề.
- `GET /api/system/logs`: Xem danh sách nhật ký hệ thống (hỗ trợ lọc `level`, `module`, tìm kiếm).
- `GET /api/system/logs/stats`: Thống kê số lượng log theo từng cấp độ.
- `DELETE /api/system/logs`: Xóa sạch nhật ký hệ thống (Admin).
- `GET /api/system/logs/export`: Xuất toàn bộ nhật ký hệ thống ra tệp tin JSON.

---

## Cấu trúc Thư mục Dự án

```
d:\Arenacode\
├── backend/
│   ├── __init__.py
│   ├── auth.py             # Băm mật khẩu PBKDF2-HMAC-SHA256, xác thực phiên làm việc
│   ├── config.py           # Quản lý cấu hình CSDL SQLite/PostgreSQL, Redis, Sandbox limits
│   ├── database.py         # Module CSDL hợp nhất (PostgreSQL & SQLite), CRUD toàn diện
│   ├── judge.py            # Sandbox Engine (Docker & Process Jail, CE/RTE check, AI Rubric, AST Winnowing)
│   ├── models.py           # Định nghĩa Pydantic Schemas (User, Submission, Contest, Problem, Log, Config)
│   ├── problems.py         # Ngân hàng đề bài cơ sở và đồng bộ CSDL
│   ├── create_portals.py   # Script tự động sinh các cổng giao diện độc lập (student, teacher, admin)
│   └── main.py             # FastAPI App, CORS Middleware, hơn 40 RESTful Endpoints
├── codearena.db            # Cơ sở dữ liệu SQLite cục bộ (tự động khởi tạo khi chạy)
├── render.yaml             # Blueprint triển khai tự động trên Render Cloud
├── Dockerfile              # Dockerfile đóng gói ứng dụng container cho production
├── Procfile                # Khởi chạy Uvicorn trên nền tảng PaaS
├── .env.example            # Mẫu thiết lập biến môi trường
├── index.html              # Cổng chính thích ứng toàn diện (Omni Portal)
├── student.html            # Cổng chuyên biệt dành cho Sinh viên (Student Portal)
├── teacher.html            # Cổng chuyên biệt dành cho Giảng viên (Teacher Portal)
├── admin.html              # Cổng chuyên biệt dành cho Quản trị viên (Admin Portal)
├── requirements.txt        # Danh mục thư viện Python (fastapi, uvicorn, pydantic, psycopg2-binary...)
├── run_server.py           # Script chạy máy chủ FastAPI (Port 8000)
└── start.bat               # Script khởi động nhanh 1-Click trên Windows
```

---

*Hệ thống được phát triển và tối ưu cho đề tài Bài tập lớn môn Phát triển Dự án CNTT - Khoa Công nghệ Thông tin, Trường Đại học Công nghiệp Hà Nội.*
