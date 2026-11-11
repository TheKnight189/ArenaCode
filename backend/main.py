import os
import secrets
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from backend.database import (
    init_db,
    get_user_by_id,
    get_user_by_email,
    list_users,
    create_user,
    update_user,
    delete_user,
    toggle_user_status,
    get_stats,
    list_submissions,
    get_submission_by_id,
    check_student_problem_submission,
    create_submission,
    grade_submission,
    delete_submission,
    list_all_codes_for_problem,
    list_contests,
    get_contest_by_id,
    create_contest,
    cancel_contest,
    get_db_status
)
from backend.models import (
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginRequest,
    LoginResponse,
    StatsResponse,
    ResetPasswordRequest,
    JudgeRunRequest,
    JudgeRunResponse,
    JudgeSubmitRequest,
    SubmissionResponse,
    GradeSubmissionRequest,
    ContestCreate,
    ContestResponse
)
from backend.auth import verify_password
from backend.config import get_ai_config, save_gemini_key
from backend.judge import execute_code, evaluate_submission
from backend.problems import PROBLEMS_DATA

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HTML_PATH = os.path.join(BASE_DIR, "index.html")
STUDENT_HTML_PATH = os.path.join(BASE_DIR, "student.html")
TEACHER_HTML_PATH = os.path.join(BASE_DIR, "teacher.html")
ADMIN_HTML_PATH = os.path.join(BASE_DIR, "admin.html")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and seed initial data on startup
    init_db()
    yield

app = FastAPI(
    title="CodeArena - Backend API Quản trị & Sandbox",
    description="Hệ thống API RESTful phục vụ xác thực người dùng, phân quyền RBAC, Sandbox Online Judge và quản lý kỳ thi cho CodeArena",
    version="2.2.0",
    lifespan=lifespan
)

# Enable CORS for frontend local and web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", summary="Trang chủ CodeArena Frontend (Tự động thích ứng vai trò)")
async def serve_frontend():
    if os.path.exists(INDEX_HTML_PATH):
        return FileResponse(INDEX_HTML_PATH)
    return JSONResponse({"message": "CodeArena Backend API is running. index.html not found."})

@app.get("/student", summary="Cổng Sinh Viên chuyên biệt (Student Portal)")
async def serve_student():
    if os.path.exists(STUDENT_HTML_PATH):
        return FileResponse(STUDENT_HTML_PATH)
    return FileResponse(INDEX_HTML_PATH)

@app.get("/teacher", summary="Cổng Giảng Viên chuyên biệt (Teacher Portal)")
async def serve_teacher():
    if os.path.exists(TEACHER_HTML_PATH):
        return FileResponse(TEACHER_HTML_PATH)
    return FileResponse(INDEX_HTML_PATH)

@app.get("/admin", summary="Cổng Quản Trị Viên chuyên biệt (Admin Portal)")
async def serve_admin():
    if os.path.exists(ADMIN_HTML_PATH):
        return FileResponse(ADMIN_HTML_PATH)
    return FileResponse(INDEX_HTML_PATH)

@app.get("/api/health", summary="Kiểm tra trạng thái máy chủ & CSDL")
async def health_check():
    stats = get_stats()
    db_status = get_db_status()
    return {
        "status": "healthy",
        "service": "CodeArena Backend API",
        "version": "2.2.0",
        "database": db_status["label"],
        "db_details": db_status,
        "total_accounts": stats["total"],
        "sandbox_engine": "Python 3 Native Sandbox"
    }

@app.get("/api/stats", response_model=StatsResponse, summary="Thống kê tài khoản hệ thống")
async def get_system_stats():
    return get_stats()

@app.get("/api/config/ai-status", summary="Kiểm tra trạng thái mô hình AI thẩm định mã nguồn")
async def get_ai_status():
    return get_ai_config()

@app.post("/api/config/gemini-key", summary="Cập nhật Google Gemini API Key")
async def update_gemini_key(req: dict):
    key = req.get("api_key", "").strip()
    if not key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vui lòng cung cấp API Key hợp lệ!")
    saved = save_gemini_key(key)
    if not saved:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Không thể lưu API Key vào hệ thống!")
    return {"message": "Đã kích hoạt Google Gemini AI thành công!", "provider": "Google Gemini 1.5 Flash", "is_ai_real": True}

# ========================================================
# AUTHENTICATION ENDPOINTS
# ========================================================
@app.post("/api/auth/login", response_model=LoginResponse, summary="Đăng nhập tài khoản")
async def login(req: LoginRequest):
    user = get_user_by_email(req.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác!"
        )

    if not verify_password(req.password, user["password_hash"], user["salt"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác!"
        )

    if user["status"] == "locked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị KHÓA bởi Quản trị viên. Vui lòng liên hệ Admin để được hỗ trợ!"
        )

    token = f"token_{user['id']}_{secrets.token_hex(12)}"

    user_resp = UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        role=user["role"],
        avatar=user["avatar"],
        status=user["status"],
        created_at=user["created_at"],
        updated_at=user["updated_at"]
    )

    return LoginResponse(
        user=user_resp,
        token=token,
        message=f"Đăng nhập thành công với vai trò {user['role']}!"
    )

# ========================================================
# ONLINE JUDGE ENGINE ENDPOINTS
# ========================================================
@app.post("/api/judge/run", response_model=JudgeRunResponse, summary="Chạy thử code trên Sandbox (Run Code)")
async def judge_run(req: JudgeRunRequest):
    """
    Executes Python source code in an isolated subprocess with stdout/stderr capture.
    """
    res = execute_code(
        code=req.code,
        language=req.language,
        stdin=req.stdin or "",
        timeout=3.0
    )
    return res

@app.post("/api/judge/submit", response_model=SubmissionResponse, summary="Nộp bài chấm điểm (Submit Code)")
async def judge_submit(req: JudgeSubmitRequest):
    """
    Submits code to the judge: evaluates test cases, computes AST similarity against
    existing submissions, calculates scores, and persists to the database.
    Quy tắc: Học sinh/Sinh viên chỉ được nộp bài 1 lần duy nhất cho mỗi bài tập.
    """
    # 0. Quy tắc nghiệp vụ: Mỗi học sinh chỉ được nộp bài 1 lần cho mỗi bài
    user = get_user_by_id(req.student_id)
    is_student = not user or (str(user.get("role", "")).lower() in ["student", "sinh viên", "sinh vien"])
    if is_student:
        existing_sub = check_student_problem_submission(req.student_id, req.problem_id)
        if existing_sub:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sinh viên {req.student_name} ({req.student_id}) đã nộp bài cho bài tập [{req.problem_name or req.problem_id}] rồi (Mã bài nộp: {existing_sub['id']})! Theo quy chế thi, mỗi học sinh chỉ được phép nộp bài 1 lần duy nhất cho mỗi bài."
            )

    # 1. Fetch previous submissions for plagiarism check
    existing_codes = list_all_codes_for_problem(req.problem_id)
    
    # 2. Evaluate
    verdict = evaluate_submission(
        problem_id=req.problem_id,
        code=req.code,
        language=req.language,
        existing_codes=existing_codes
    )

    # 3. Create submission in DB
    sub_id = f"SUB-{secrets.randbelow(9000) + 1000}"
    sub_data = {
        "id": sub_id,
        "student_id": req.student_id,
        "student_name": req.student_name,
        "problem_id": req.problem_id,
        "problem_name": req.problem_name,
        "language": req.language if "python" not in req.language.lower() else "Python 3",
        "code": req.code,
        "status": verdict["status"],
        "test_passed": verdict["test_passed"],
        "runtime": verdict["runtime"],
        "memory": verdict["memory"],
        "score": verdict["score"],
        "ai_score": verdict["ai_score"],
        "ai_rubric": verdict["ai_rubric"],
        "similarity_rate": verdict["similarity_rate"],
        "feedback": "Đang chờ Giảng viên chấm điểm và công bố nhận xét...",
        "is_graded_by_teacher": False,
        "graded_by": None,
        "graded_at": None
    }
    created = create_submission(sub_data)
    return created

# ========================================================
# SUBMISSIONS MANAGEMENT (TEACHER & RESULTS PORTAL)
# ========================================================
@app.get("/api/submissions", response_model=list[SubmissionResponse], summary="Lấy danh sách bài nộp")
async def get_submissions(
    student_id: Optional[str] = Query(None, description="Lọc theo mã sinh viên"),
    problem_id: Optional[str] = Query(None, description="Lọc theo mã bài tập"),
    status: Optional[str] = Query(None, description="Lọc theo trạng thái chấm: graded, pending, Gian lận, v.v."),
    q: Optional[str] = Query(None, description="Tìm kiếm theo tên SV, mã SV, mã bài nộp")
):
    return list_submissions(student_id=student_id, problem_id=problem_id, status=status, q=q)

@app.get("/api/submissions/{sub_id}", response_model=SubmissionResponse, summary="Xem chi tiết một bài nộp")
async def get_submission_detail(sub_id: str):
    sub = get_submission_by_id(sub_id)
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài nộp!")
    return sub

@app.put("/api/submissions/{sub_id}/grade", response_model=SubmissionResponse, summary="Giảng viên chấm điểm bài nộp")
async def teacher_grade_submission(sub_id: str, req: GradeSubmissionRequest):
    existing = get_submission_by_id(sub_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài nộp để chấm điểm!")

    updated = grade_submission(
        sub_id=sub_id,
        score=req.score,
        status=req.status,
        feedback=req.feedback,
        teacher_name=req.teacher_name or "TS. Nguyễn Thị Hoa Huệ"
    )
    return updated

@app.delete("/api/submissions/{sub_id}", summary="Xóa bài làm của sinh viên")
async def delete_submission_endpoint(sub_id: str):
    existing = get_submission_by_id(sub_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài làm cần xóa!")
    success = delete_submission(sub_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Xóa bài làm thất bại!")
    return {
        "message": f"Đã xóa bài làm {sub_id} của sinh viên {existing.get('student_name', '')} thành công!",
        "deleted_id": sub_id,
        "student_id": existing.get("student_id"),
        "problem_id": existing.get("problem_id")
    }

@app.post("/api/submissions/{sub_id}/rejudge", response_model=SubmissionResponse, summary="Chấm lại một bài nộp")
async def rejudge_submission(sub_id: str):
    existing = get_submission_by_id(sub_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài nộp!")

    other_codes = [c for c in list_all_codes_for_problem(existing["problem_id"]) if c != existing["code"]]
    verdict = evaluate_submission(
        problem_id=existing["problem_id"],
        code=existing["code"],
        language=existing["language"],
        existing_codes=other_codes
    )

    updated = grade_submission(
        sub_id=sub_id,
        score=verdict["score"],
        status=verdict["status"],
        feedback=f"Chấm lại tự động bởi AI Sandbox: {verdict['ai_rubric']}"
    )
    return updated

@app.post("/api/submissions/batch-rejudge", summary="Chấm lại toàn bộ bài nộp của lớp")
async def batch_rejudge_all():
    all_subs = list_submissions()
    rejudged_count = 0
    for s in all_subs:
        other_codes = [c for c in list_all_codes_for_problem(s["problem_id"]) if c != s["code"]]
        verdict = evaluate_submission(
            problem_id=s["problem_id"],
            code=s["code"],
            language=s["language"],
            existing_codes=other_codes
        )
        grade_submission(
            sub_id=s["id"],
            score=verdict["score"],
            status=verdict["status"],
            feedback=f"Chấm lại tự động: {verdict['ai_rubric']}"
        )
        rejudged_count += 1
    return {"message": f"Đã chấm lại thành công {rejudged_count} bài nộp!", "total": rejudged_count}

# ========================================================
# CONTESTS MANAGEMENT
# ========================================================
@app.get("/api/contests", response_model=list[ContestResponse], summary="Danh sách các kỳ thi")
async def get_contests():
    return list_contests()

@app.get("/api/contests/{contest_id}", response_model=ContestResponse, summary="Chi tiết kỳ thi")
async def get_contest(contest_id: str):
    c = get_contest_by_id(contest_id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy kỳ thi!")
    return c

@app.post("/api/contests", response_model=ContestResponse, status_code=status.HTTP_201_CREATED, summary="Tạo kỳ thi mới")
async def create_new_contest(req: ContestCreate):
    created = create_contest(req.model_dump())
    return created

@app.post("/api/contests/{contest_id}/cancel", response_model=ContestResponse, summary="Hủy kỳ thi")
async def cancel_existing_contest(contest_id: str):
    c = get_contest_by_id(contest_id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy kỳ thi!")
    updated = cancel_contest(contest_id)
    return updated

# ========================================================
# PROBLEMS REPOSITORY ENDPOINT
# ========================================================
@app.get("/api/problems", summary="Danh sách bài tập và test case")
async def get_problems():
    return PROBLEMS_DATA

@app.get("/api/problems/{problem_id}", summary="Chi tiết một bài tập")
async def get_problem(problem_id: str):
    p = PROBLEMS_DATA.get(problem_id)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài tập!")
    return p

# ========================================================
# USER MANAGEMENT (CRUD)
# ========================================================
@app.get("/api/users", response_model=list[UserResponse], summary="Lấy danh sách người dùng")
async def get_users(
    q: Optional[str] = Query(None, description="Tìm theo tên, email hoặc mã tài khoản"),
    role: Optional[str] = Query(None, description="Lọc theo vai trò: Admin, Giáo viên, Sinh viên"),
    status: Optional[str] = Query(None, description="Lọc theo trạng thái: active, locked")
):
    users = list_users(q=q, role=role, status=status)
    return users

@app.get("/api/users/{user_id}", response_model=UserResponse, summary="Xem chi tiết người dùng")
async def get_user_detail(user_id: str):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản!")
    return user

@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Tạo tài khoản mới")
async def add_user(req: UserCreate):
    if get_user_by_id(req.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã tài khoản '{req.id}' đã tồn tại trong hệ thống!"
        )

    if get_user_by_email(str(req.email)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{req.email}' đã được đăng ký cho tài khoản khác!"
        )

    valid_roles = ["Admin", "Giáo viên", "Sinh viên"]
    if req.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vai trò không hợp lệ. Chọn một trong: {', '.join(valid_roles)}"
        )

    user_dict = req.model_dump()
    user_dict["email"] = str(req.email)
    created = create_user(user_dict)
    return created

@app.put("/api/users/{user_id}", response_model=UserResponse, summary="Cập nhật tài khoản")
async def edit_user(user_id: str, req: UserUpdate):
    existing = get_user_by_id(user_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản cần cập nhật!")

    if req.email and str(req.email).lower() != existing["email"].lower():
        email_check = get_user_by_email(str(req.email))
        if email_check and email_check["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{req.email}' đã được sử dụng bởi người dùng khác!"
            )

    update_dict = req.model_dump(exclude_unset=True)
    if "email" in update_dict and update_dict["email"] is not None:
        update_dict["email"] = str(update_dict["email"])

    updated = update_user(user_id, update_dict)
    return updated

@app.delete("/api/users/{user_id}", summary="Xoá tài khoản")
async def remove_user(user_id: str):
    existing = get_user_by_id(user_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản cần xoá!")

    if user_id == "ADMIN-01":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xoá tài khoản Quản trị viên gốc (ADMIN-01) để bảo đảm an toàn hệ thống!"
        )

    deleted = delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Xoá tài khoản thất bại!")

    return {"message": f"Đã xoá vĩnh viễn tài khoản {existing['name']} ({user_id}) khỏi hệ thống!", "success": True}

@app.post("/api/users/{user_id}/toggle-status", response_model=UserResponse, summary="Khóa hoặc Mở khóa tài khoản")
async def toggle_status(user_id: str):
    existing = get_user_by_id(user_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản!")

    if user_id == "ADMIN-01":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể khóa tài khoản Quản trị viên gốc (ADMIN-01)!"
        )

    updated = toggle_user_status(user_id)
    return updated

@app.post("/api/users/{user_id}/reset-password", summary="Đặt lại mật khẩu cho tài khoản")
async def reset_password(user_id: str, req: ResetPasswordRequest):
    existing = get_user_by_id(user_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản!")

    update_user(user_id, {"password": req.new_password})
    return {"message": f"Đã đặt lại mật khẩu thành công cho tài khoản {existing['name']}!", "success": True}
