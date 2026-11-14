from typing import Optional, List
from pydantic import BaseModel, Field

# ========================================================
# USER MODELS
# ========================================================
class UserBase(BaseModel):
    id: str = Field(..., min_length=2, max_length=50, description="Mã người dùng, MSSV hoặc Mã cán bộ")
    name: str = Field(..., min_length=2, max_length=100, description="Họ và tên")
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="Địa chỉ email hợp lệ")
    role: str = Field(..., description="Vai trò: Admin, Giáo viên, hoặc Sinh viên")
    status: str = Field(default="active", description="Trạng thái: active hoặc locked")

class UserCreate(UserBase):
    password: str = Field(..., min_length=3, max_length=100, description="Mật khẩu đăng nhập")
    avatar: Optional[str] = Field(default=None, description="Ký hiệu avatar (tự động tạo nếu để trống)")

class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[str] = Field(default=None, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    role: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None, min_length=3, max_length=100)
    avatar: Optional[str] = Field(default=None)

class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=3, max_length=100)

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    avatar: str
    status: str
    created_at: str
    updated_at: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    user: UserResponse
    token: str
    message: str

class StatsResponse(BaseModel):
    total: int
    admins: int
    teachers: int
    students: int
    active: int
    locked: int

# ========================================================
# JUDGE & CODE EXECUTION MODELS
# ========================================================
class JudgeRunRequest(BaseModel):
    code: str
    language: str = "python"
    stdin: Optional[str] = ""
    problem_id: Optional[str] = None

class JudgeRunResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    runtime_ms: float
    memory_mb: float
    status: str

class JudgeSubmitRequest(BaseModel):
    student_id: str
    student_name: str
    problem_id: str
    problem_name: str
    language: str = "python"
    code: str

# ========================================================
# SUBMISSION MODELS
# ========================================================
class SubmissionResponse(BaseModel):
    id: str
    student_id: str
    student_name: str
    problem_id: str
    problem_name: str
    language: str
    code: str
    status: str
    test_passed: str
    runtime: str
    memory: str
    score: str
    ai_score: str
    ai_rubric: Optional[str] = ""
    similarity_rate: float = 0.0
    feedback: Optional[str] = ""
    is_graded_by_teacher: bool = False
    graded_by: Optional[str] = None
    graded_at: Optional[str] = None
    visible_tests: Optional[str] = None
    hidden_tests: Optional[str] = None
    test_details: Optional[list] = None
    created_at: str

class GradeSubmissionRequest(BaseModel):
    score: str = Field(..., description="Điểm số (ví dụ 10.0 hoặc 0.0)")
    status: str = Field(..., description="Trạng thái (Accepted, Wrong Answer, Gian lận)")
    feedback: str = Field(..., description="Nhận xét của Giảng viên")
    teacher_name: Optional[str] = Field(default="TS. Nguyễn Thị Hoa Huệ", description="Tên giảng viên chấm")

# ========================================================
# CONTEST MODELS
# ========================================================
class ContestCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    desc: Optional[str] = ""
    creator: Optional[str] = "TS. Nguyễn Thị Hoa Huệ"
    duration_minutes: int = Field(default=120, ge=10, le=1440)
    rule: Optional[str] = "Luật ICPC (Penalty 20 phút/lần nộp sai)"
    grader_mode: Optional[str] = "hybrid"
    problems: List[str] = Field(default_factory=lambda: ["CA-101", "CA-102", "CA-103", "CA-104"])

class ContestResponse(BaseModel):
    id: str
    title: str
    desc: Optional[str]
    creator: str
    start_time: str
    duration_minutes: int
    status: str
    rule: str
    grader_mode: str
    problems: List[str]
    created_at: str
