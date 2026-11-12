import sqlite3
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from backend.auth import hash_password, generate_avatar
from backend.config import SQLITE_PATH, DATABASE_URL

logger = logging.getLogger("codearena.database")
logging.basicConfig(level=logging.INFO)

def mask_database_url(url: str) -> str:
    """Ẩn mật khẩu trong connection string khi trả về API status để bảo mật"""
    if not url:
        return ""
    try:
        if "@" in url:
            prefix, host_part = url.split("@", 1)
            if "://" in prefix:
                proto, user_pass = prefix.split("://", 1)
                user = user_pass.split(":")[0] if ":" in user_pass else user_pass
                return f"{proto}://{user}:****@{host_part}"
        return "postgresql://****"
    except Exception:
        return "postgresql://****"

class CodeArenaCursor:
    """Cursor wrapper hỗ trợ đồng thời SQLite và PostgreSQL, tự động chuẩn hóa placeholder và cú pháp"""
    def __init__(self, raw_cursor, is_postgres: bool = False):
        self.raw_cursor = raw_cursor
        self.is_postgres = is_postgres

    def execute(self, query: str, args=None):
        if self.is_postgres:
            # PostgreSQL: Giữ %s, chuẩn hóa INSERT IGNORE sang ON CONFLICT DO NOTHING, escape cột `desc`
            sql = query.replace("`desc`", '"desc"')
            if "INSERT IGNORE INTO" in sql:
                sql = sql.replace("INSERT IGNORE INTO", "INSERT INTO")
                if "ON CONFLICT" not in sql:
                    sql = sql.strip() + " ON CONFLICT DO NOTHING"
            if args is None:
                return self.raw_cursor.execute(sql)
            return self.raw_cursor.execute(sql, args)
        else:
            # SQLite: Đổi %s thành ?, INSERT IGNORE thành INSERT OR IGNORE, bỏ backtick `desc`
            sql = query.replace("%s", "?").replace("INSERT IGNORE", "INSERT OR IGNORE").replace("`desc`", "desc")
            if args is None:
                return self.raw_cursor.execute(sql)
            return self.raw_cursor.execute(sql, args)

    def fetchone(self) -> Optional[Dict[str, Any]]:
        row = self.raw_cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self) -> List[Dict[str, Any]]:
        rows = self.raw_cursor.fetchall()
        return [dict(r) for r in rows]

    @property
    def rowcount(self) -> int:
        return self.raw_cursor.rowcount

    def close(self):
        try:
            self.raw_cursor.close()
        except Exception:
            pass

class CodeArenaConnection:
    """Connection wrapper chuẩn cho CSDL SQLite & PostgreSQL"""
    def __init__(self, raw_conn, is_postgres: bool = False):
        self.raw_conn = raw_conn
        self.is_postgres = is_postgres

    def cursor(self) -> CodeArenaCursor:
        return CodeArenaCursor(self.raw_conn.cursor(), is_postgres=self.is_postgres)

    def commit(self):
        try:
            self.raw_conn.commit()
        except Exception:
            pass

    def rollback(self):
        try:
            self.raw_conn.rollback()
        except Exception:
            pass

    def close(self):
        try:
            self.raw_conn.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()

def get_db() -> CodeArenaConnection:
    """Lấy kết nối tới CSDL (ưu tiên PostgreSQL nếu có DATABASE_URL, ngược lại fallback SQLite)"""
    if DATABASE_URL:
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            pg_url = DATABASE_URL
            if pg_url.startswith("postgres://"):
                pg_url = "postgresql://" + pg_url[11:]
            conn = psycopg2.connect(pg_url, cursor_factory=RealDictCursor)
            return CodeArenaConnection(conn, is_postgres=True)
        except Exception as pge:
            logger.warning(f"⚠️ [CodeArena DB] Lỗi kết nối PostgreSQL ({pge}), chuyển sang SQLite fallback.")

    conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return CodeArenaConnection(conn, is_postgres=False)

def get_db_status() -> Dict[str, Any]:
    """Trả về trạng thái kết nối CSDL phục vụ API /api/health và giao diện"""
    if DATABASE_URL:
        return {
            "engine": "PostgreSQL",
            "connected": True,
            "url": mask_database_url(DATABASE_URL),
            "label": "Render PostgreSQL Cloud Database",
            "mode": "cloud",
            "message": "CSDL PostgreSQL trên Render đang hoạt động ổn định"
        }
    return {
        "engine": "SQLite",
        "connected": True,
        "file": SQLITE_PATH,
        "label": "SQLite Database (Local)",
        "mode": "standalone",
        "message": "CSDL SQLite đang hoạt động ổn định"
    }

def _init_postgres_schema(cursor):
    """Tạo schema bảng dữ liệu trên PostgreSQL"""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(100) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role VARCHAR(50) NOT NULL,
        avatar VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        created_at VARCHAR(50) NOT NULL,
        updated_at VARCHAR(50) NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id VARCHAR(100) PRIMARY KEY,
        student_id VARCHAR(100) NOT NULL,
        student_name VARCHAR(255) NOT NULL,
        problem_id VARCHAR(100) NOT NULL,
        problem_name VARCHAR(255) NOT NULL,
        language VARCHAR(50) NOT NULL,
        code TEXT NOT NULL,
        status VARCHAR(50) NOT NULL,
        test_passed VARCHAR(50) NOT NULL,
        runtime VARCHAR(50) NOT NULL,
        memory VARCHAR(50) NOT NULL,
        score VARCHAR(50) NOT NULL,
        ai_score VARCHAR(50) NOT NULL,
        ai_rubric TEXT,
        similarity_rate DOUBLE PRECISION DEFAULT 0.0,
        feedback TEXT,
        is_graded_by_teacher INTEGER NOT NULL DEFAULT 0,
        graded_by VARCHAR(255),
        graded_at VARCHAR(50),
        created_at VARCHAR(50) NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contests (
        id VARCHAR(100) PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        "desc" TEXT,
        creator VARCHAR(255) NOT NULL,
        start_time VARCHAR(50) NOT NULL,
        duration_minutes INTEGER NOT NULL DEFAULT 120,
        status VARCHAR(50) NOT NULL DEFAULT 'Đang diễn ra',
        rule TEXT NOT NULL,
        grader_mode VARCHAR(50) NOT NULL DEFAULT 'hybrid',
        problems TEXT NOT NULL,
        created_at VARCHAR(50) NOT NULL
    );
    """)

def _init_sqlite_schema(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL,
        avatar TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id TEXT PRIMARY KEY,
        student_id TEXT NOT NULL,
        student_name TEXT NOT NULL,
        problem_id TEXT NOT NULL,
        problem_name TEXT NOT NULL,
        language TEXT NOT NULL,
        code TEXT NOT NULL,
        status TEXT NOT NULL,
        test_passed TEXT NOT NULL,
        runtime TEXT NOT NULL,
        memory TEXT NOT NULL,
        score TEXT NOT NULL,
        ai_score TEXT NOT NULL,
        ai_rubric TEXT,
        similarity_rate REAL DEFAULT 0.0,
        feedback TEXT,
        is_graded_by_teacher INTEGER NOT NULL DEFAULT 0,
        graded_by TEXT,
        graded_at TEXT,
        created_at TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contests (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        `desc` TEXT,
        creator TEXT NOT NULL,
        start_time TEXT NOT NULL,
        duration_minutes INTEGER NOT NULL DEFAULT 120,
        status TEXT NOT NULL DEFAULT 'Đang diễn ra',
        rule TEXT NOT NULL,
        grader_mode TEXT NOT NULL DEFAULT 'hybrid',
        problems TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

def _seed_data_if_needed(cursor, conn):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Kiểm tra Admin
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'Admin'")
    row = cursor.fetchone()
    count = row["count"] if row else 0

    if count == 0:
        seed_users = [
            {
                "id": "ADMIN-01",
                "name": "Quản trị viên Hệ thống",
                "email": "admin@haui.edu.vn",
                "password": "admin",
                "role": "Admin",
                "avatar": "AD",
                "status": "active"
            },
            {
                "id": "GV-HAUI-01",
                "name": "TS. Nguyễn Thị Hoa Huệ",
                "email": "gv.huenth@haui.edu.vn",
                "password": "password123",
                "role": "Giáo viên",
                "avatar": "HH",
                "status": "active"
            },
            {
                "id": "20240606239",
                "name": "Hoàng Anh Tú",
                "email": "20240606239@sv.haui.edu.vn",
                "password": "password123",
                "role": "Sinh viên",
                "avatar": "AT",
                "status": "active"
            },
            {
                "id": "20240606240",
                "name": "Nguyễn Kim Huy",
                "email": "20240606240@sv.haui.edu.vn",
                "password": "password123",
                "role": "Sinh viên",
                "avatar": "KH",
                "status": "active"
            },
            {
                "id": "20240606241",
                "name": "Nguyễn Cảnh Hải",
                "email": "20240606241@sv.haui.edu.vn",
                "password": "password123",
                "role": "Sinh viên",
                "avatar": "CH",
                "status": "active"
            },
            {
                "id": "20240606242",
                "name": "Lưu Quang Huy",
                "email": "20240606242@sv.haui.edu.vn",
                "password": "password123",
                "role": "Sinh viên",
                "avatar": "QH",
                "status": "active"
            },
            {
                "id": "20240606243",
                "name": "Hoàng Thái Hưng",
                "email": "20240606243@sv.haui.edu.vn",
                "password": "password123",
                "role": "Sinh viên",
                "avatar": "TH",
                "status": "active"
            }
        ]

        for u in seed_users:
            pwd_hash, salt = hash_password(u["password"])
            cursor.execute("""
            INSERT IGNORE INTO users (id, name, email, password_hash, salt, role, avatar, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (u["id"], u["name"], u["email"], pwd_hash, salt, u["role"], u["avatar"], u["status"], now, now))
        conn.commit()

    # Kiểm tra submissions
    cursor.execute("SELECT COUNT(*) as count FROM submissions")
    s_row = cursor.fetchone()
    s_count = s_row["count"] if s_row else 0

    if s_count == 0:
        seed_subs = [
            {
                "id": "SUB-4080",
                "student_id": "20240606239",
                "student_name": "Trần Đăng Khoa",
                "problem_id": "CA-102",
                "problem_name": "Dãy con tăng dài nhất (LIS)",
                "language": "Python 3",
                "code": "import bisect\n\ndef lengthOfLIS(nums):\n    tails = []\n    for x in nums:\n        idx = bisect.bisect_left(tails, x)\n        if idx == len(tails):\n            tails.append(x)\n        else:\n            tails[idx] = x\n    return len(tails)",
                "status": "Accepted",
                "test_passed": "5/5",
                "runtime": "32 ms",
                "memory": "14.4 MB",
                "score": "10.0",
                "ai_score": "10.0",
                "ai_rubric": "Đáp ứng 100% yêu cầu đề bài; Tối ưu Binary Search kết hợp DP O(N log N); Code chuẩn.",
                "similarity_rate": 0.0,
                "feedback": "Giảng viên nhận xét: Lời giải mẫu mực, tối ưu độ phức tạp tốt nhất O(N log N). Điểm tối đa.",
                "is_graded_by_teacher": 1,
                "graded_by": "TS. Nguyễn Thị Hoa Huệ",
                "graded_at": "14:15:00",
                "created_at": now
            },
            {
                "id": "SUB-4081",
                "student_id": "20240606241",
                "student_name": "Nguyễn Cảnh Hải",
                "problem_id": "CA-101",
                "problem_name": "Tìm cặp số có tổng bằng K (Two Sum)",
                "language": "Python 3",
                "code": "def twoSum(nums, target):\n    mp = {}\n    for i, x in enumerate(nums):\n        if target - x in mp:\n            return [mp[target - x], i]\n        mp[x] = i\n    return []",
                "status": "Accepted",
                "test_passed": "5/5",
                "runtime": "28 ms",
                "memory": "14.2 MB",
                "score": "10.0",
                "ai_score": "10.0",
                "ai_rubric": "Đáp ứng 100% yêu cầu đề bài; Tối ưu tra cứu Hash Map O(N); Code sạch sẽ.",
                "similarity_rate": 12.4,
                "feedback": "Giảng viên nhận xét: Thuật toán tra cứu Hash Map O(N) rất tối ưu, xử lý tốt trường hợp mảng có phần tử trùng. Điểm tối đa.",
                "is_graded_by_teacher": 1,
                "graded_by": "TS. Nguyễn Thị Hoa Huệ",
                "graded_at": "14:20:00",
                "created_at": now
            },
            {
                "id": "SUB-4082",
                "student_id": "20240606240",
                "student_name": "Nguyễn Kim Huy",
                "problem_id": "CA-102",
                "problem_name": "Dãy con tăng dài nhất (LIS)",
                "language": "Python 3",
                "code": "import bisect\ndef solve_lis(arr):\n    sub = []\n    for item in arr:\n        pos = bisect.bisect_left(sub, item)\n        if pos == len(sub): sub.append(item)\n        else: sub[pos] = item\n    return len(sub)",
                "status": "Gian lận",
                "test_passed": "5/5",
                "runtime": "39 ms",
                "memory": "14.8 MB",
                "score": "0.0",
                "ai_score": "0.0",
                "ai_rubric": "Vi phạm quy chế liêm chính học thuật: Độ trùng lặp 94.6% với bài nộp SUB-4080.",
                "similarity_rate": 94.6,
                "feedback": "Giảng viên nhận xét: Phát hiện sao chép mã nguồn 94.6% (vượt ngưỡng an toàn 75%). Đặt 0 điểm.",
                "is_graded_by_teacher": 1,
                "graded_by": "TS. Nguyễn Thị Hoa Huệ",
                "graded_at": "14:30:15",
                "created_at": now
            },
            {
                "id": "SUB-4083",
                "student_id": "20240606242",
                "student_name": "Lê Hoàng Long",
                "problem_id": "CA-102",
                "problem_name": "Dãy con tăng dài nhất (LIS)",
                "language": "Python 3",
                "code": "def lengthOfLIS(nums):\n    if not nums:\n        return 0\n    dp = [1] * len(nums)\n    for i in range(len(nums)):\n        for j in range(i):\n            if nums[i] > nums[j]:\n                dp[i] = max(dp[i], dp[j] + 1)\n    return max(dp)",
                "status": "Accepted",
                "test_passed": "5/5",
                "runtime": "85 ms",
                "memory": "14.5 MB",
                "score": "8.5",
                "ai_score": "8.5",
                "ai_rubric": "Đáp ứng đúng yêu cầu bài toán; Giải thuật Quy hoạch động cơ bản O(N^2).",
                "similarity_rate": 18.2,
                "feedback": "Giảng viên nhận xét: Thuật toán quy hoạch động đúng, nên tối ưu thêm bằng Binary Search O(N log N).",
                "is_graded_by_teacher": 1,
                "graded_by": "TS. Nguyễn Thị Hoa Huệ",
                "graded_at": "14:35:00",
                "created_at": now
            }
        ]
        for s in seed_subs:
            cursor.execute("""
            INSERT IGNORE INTO submissions (
                id, student_id, student_name, problem_id, problem_name, language, code, status,
                test_passed, runtime, memory, score, ai_score, ai_rubric, similarity_rate,
                feedback, is_graded_by_teacher, graded_by, graded_at, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                s["id"], s["student_id"], s["student_name"], s["problem_id"], s["problem_name"],
                s["language"], s["code"], s["status"], s["test_passed"], s["runtime"], s["memory"],
                s["score"], s["ai_score"], s["ai_rubric"], s["similarity_rate"], s["feedback"],
                s["is_graded_by_teacher"], s["graded_by"], s["graded_at"], s["created_at"]
            ))
        conn.commit()

    # Kiểm tra contests
    cursor.execute("SELECT COUNT(*) as count FROM contests")
    c_row = cursor.fetchone()
    c_count = c_row["count"] if c_row else 0

    if c_count == 0:
        cursor.execute("""
        INSERT IGNORE INTO contests (
            id, title, `desc`, creator, start_time, duration_minutes, status, rule, grader_mode, problems, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            "CONTEST-01",
            "HaUI IT Code Challenge 2026 - Kỳ thi Lập trình K16",
            "Kỳ thi chính thức của Khoa Công nghệ Thông tin - HaUI.",
            "TS. Nguyễn Thị Hoa Huệ",
            now,
            120,
            "Đang diễn ra",
            "Luật ICPC (Penalty 20 phút/lần nộp sai)",
            "hybrid",
            json.dumps(["CA-101", "CA-102", "CA-103", "CA-104"]),
            now
        ))
        conn.commit()

def init_db():
    """Khởi tạo CSDL chính thức (ưu tiên PostgreSQL nếu có DATABASE_URL trên Render, fallback SQLite khi chạy cục bộ)"""
    if DATABASE_URL:
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            pg_url = DATABASE_URL
            if pg_url.startswith("postgres://"):
                pg_url = "postgresql://" + pg_url[11:]
            conn = psycopg2.connect(pg_url, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            _init_postgres_schema(cursor)
            conn.commit()
            wrapped_conn = CodeArenaConnection(conn, is_postgres=True)
            wrapped_cursor = CodeArenaCursor(cursor, is_postgres=True)
            _seed_data_if_needed(wrapped_cursor, wrapped_conn)
            conn.commit()
            conn.close()
            logger.info("🐘 [CodeArena DB] CSDL PostgreSQL trên Render/Cloud đã kết nối và khởi tạo thành công!")
            return
        except Exception as pge:
            logger.warning(f"⚠️ [CodeArena DB] Không thể khởi tạo PostgreSQL ({pge}), chuyển sang SQLite fallback.")

    try:
        conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        _init_sqlite_schema(cursor)
        wrapped_conn = CodeArenaConnection(conn, is_postgres=False)
        wrapped_cursor = CodeArenaCursor(cursor, is_postgres=False)
        _seed_data_if_needed(wrapped_cursor, wrapped_conn)
        conn.commit()
        conn.close()
        logger.info(f"📁 [CodeArena DB] CSDL SQLite đã sẵn sàng: {SQLITE_PATH}")
    except Exception as sqle:
        logger.error(f"❌ [CodeArena DB] Lỗi nghiêm trọng khi khởi tạo CSDL SQLite: {sqle}")
        raise sqle

# ========================================================
# USER CRUD FUNCTIONS
# ========================================================
def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(%s)", (email,))
    row = cursor.fetchone()
    conn.close()
    return row

def list_users(q: str = None, role: str = None, status: str = None) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT id, name, email, role, avatar, status, created_at, updated_at FROM users WHERE 1=1"
    params = []

    if isinstance(role, str) and role.strip() and role.lower() != "all":
        query += " AND role = %s"
        params.append(role.strip())

    if isinstance(status, str) and status.strip() and status.lower() != "all":
        query += " AND status = %s"
        params.append(status.strip())

    if isinstance(q, str) and q.strip():
        search = f"%{q.strip()}%"
        query += " AND (name LIKE %s OR email LIKE %s OR id LIKE %s)"
        params.extend([search, search, search])

    query += " ORDER BY CASE role WHEN 'Admin' THEN 1 WHEN 'Giáo viên' THEN 2 ELSE 3 END, created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def create_user(user_data: dict) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    avatar = user_data.get("avatar") or generate_avatar(user_data["name"])
    pwd_hash, salt = hash_password(user_data["password"])

    cursor.execute("""
    INSERT INTO users (id, name, email, password_hash, salt, role, avatar, status, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_data["id"],
        user_data["name"],
        user_data["email"],
        pwd_hash,
        salt,
        user_data["role"],
        avatar,
        user_data.get("status", "active"),
        now,
        now
    ))
    conn.commit()
    conn.close()
    return get_user_by_id(user_data["id"])

def update_user(user_id: str, update_data: dict) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    fields = []
    params = []

    if "name" in update_data and update_data["name"] is not None:
        fields.append("name = %s")
        params.append(update_data["name"])
        if not update_data.get("avatar"):
            fields.append("avatar = %s")
            params.append(generate_avatar(update_data["name"]))

    if "email" in update_data and update_data["email"] is not None:
        fields.append("email = %s")
        params.append(update_data["email"])

    if "role" in update_data and update_data["role"] is not None:
        fields.append("role = %s")
        params.append(update_data["role"])

    if "status" in update_data and update_data["status"] is not None:
        fields.append("status = %s")
        params.append(update_data["status"])

    if "avatar" in update_data and update_data["avatar"] is not None:
        fields.append("avatar = %s")
        params.append(update_data["avatar"])

    if "password" in update_data and update_data["password"]:
        pwd_hash, salt = hash_password(update_data["password"])
        fields.append("password_hash = %s")
        fields.append("salt = %s")
        params.extend([pwd_hash, salt])

    if not fields:
        conn.close()
        return get_user_by_id(user_id)

    fields.append("updated_at = %s")
    params.append(now)

    params.append(user_id)
    query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    return get_user_by_id(user_id)

def delete_user(user_id: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def toggle_user_status(user_id: str) -> Optional[Dict[str, Any]]:
    user = get_user_by_id(user_id)
    if not user:
        return None
    new_status = "locked" if user["status"] == "active" else "active"
    return update_user(user_id, {"status": new_status})

def get_stats() -> Dict[str, int]:
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM users")
    t_row = cursor.fetchone()
    total = t_row["total"] if t_row else 0

    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'Admin'")
    a_row = cursor.fetchone()
    admins = a_row["cnt"] if a_row else 0

    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'Giáo viên'")
    g_row = cursor.fetchone()
    teachers = g_row["cnt"] if g_row else 0

    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'Sinh viên'")
    s_row = cursor.fetchone()
    students = s_row["cnt"] if s_row else 0

    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE status = 'active'")
    ac_row = cursor.fetchone()
    active = ac_row["cnt"] if ac_row else 0

    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE status = 'locked'")
    lk_row = cursor.fetchone()
    locked = lk_row["cnt"] if lk_row else 0

    conn.close()
    return {
        "total": total,
        "admins": admins,
        "teachers": teachers,
        "students": students,
        "active": active,
        "locked": locked
    }

# ========================================================
# SUBMISSION CRUD FUNCTIONS
# ========================================================
def list_submissions(student_id: str = None, problem_id: str = None, status: str = None, q: str = None) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM submissions WHERE 1=1"
    params = []

    if isinstance(student_id, str) and student_id.strip():
        query += " AND student_id = %s"
        params.append(student_id.strip())

    if isinstance(problem_id, str) and problem_id.strip() and problem_id != "all":
        query += " AND problem_id = %s"
        params.append(problem_id.strip())

    if isinstance(status, str) and status.strip() and status != "all":
        status_clean = status.strip()
        if status_clean == "graded":
            query += " AND is_graded_by_teacher = 1"
        elif status_clean == "pending":
            query += " AND is_graded_by_teacher = 0"
        elif status_clean == "Gian lận":
            query += " AND (status = 'Gian lận' OR similarity_rate >= 75.0)"
        else:
            query += " AND status = %s"
            params.append(status_clean)

    if isinstance(q, str) and q.strip():
        search = f"%{q.strip()}%"
        query += " AND (student_name LIKE %s OR student_id LIKE %s OR id LIKE %s)"
        params.extend([search, search, search])

    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for d in rows:
        d["is_graded_by_teacher"] = bool(d.get("is_graded_by_teacher", 0))
        d["similarity_rate"] = float(d.get("similarity_rate") or 0.0)
        result.append(d)
    return result

def get_submission_by_id(sub_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM submissions WHERE id = %s", (sub_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    row["is_graded_by_teacher"] = bool(row.get("is_graded_by_teacher", 0))
    row["similarity_rate"] = float(row.get("similarity_rate") or 0.0)
    return row

def check_student_problem_submission(student_id: str, problem_id: str) -> Optional[Dict[str, Any]]:
    """Kiểm tra xem sinh viên đã từng nộp bài cho bài tập này chưa (Chính sách 1 lần nộp duy nhất/bài)"""
    if not student_id or not problem_id:
        return None
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM submissions WHERE student_id = %s AND problem_id = %s ORDER BY created_at DESC LIMIT 1",
        (student_id.strip(), problem_id.strip())
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    row["is_graded_by_teacher"] = bool(row.get("is_graded_by_teacher", 0))
    row["similarity_rate"] = float(row.get("similarity_rate") or 0.0)
    return row

def create_submission(sub_data: dict) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO submissions (
        id, student_id, student_name, problem_id, problem_name, language, code, status,
        test_passed, runtime, memory, score, ai_score, ai_rubric, similarity_rate,
        feedback, is_graded_by_teacher, graded_by, graded_at, created_at
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        sub_data["id"],
        sub_data["student_id"],
        sub_data["student_name"],
        sub_data["problem_id"],
        sub_data["problem_name"],
        sub_data.get("language", "Python 3"),
        sub_data["code"],
        sub_data.get("status", "Accepted"),
        sub_data.get("test_passed", "3/3"),
        sub_data.get("runtime", "25 ms"),
        sub_data.get("memory", "14.2 MB"),
        sub_data.get("score", "10.0"),
        sub_data.get("ai_score", "9.5"),
        sub_data.get("ai_rubric", ""),
        sub_data.get("similarity_rate", 0.0),
        sub_data.get("feedback", "Đang chờ Giảng viên chấm điểm và công bố nhận xét..."),
        1 if sub_data.get("is_graded_by_teacher") else 0,
        sub_data.get("graded_by"),
        sub_data.get("graded_at"),
        now
    ))
    conn.commit()
    conn.close()
    return get_submission_by_id(sub_data["id"])

def grade_submission(sub_id: str, score: str, status: str, feedback: str, teacher_name: str = "TS. Nguyễn Thị Hoa Huệ") -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    now_time = datetime.now().strftime("%H:%M:%S")

    cursor.execute("""
    UPDATE submissions SET
        score = %s,
        status = %s,
        feedback = %s,
        is_graded_by_teacher = 1,
        graded_by = %s,
        graded_at = %s
    WHERE id = %s
    """, (score, status, feedback, teacher_name, now_time, sub_id))
    conn.commit()
    conn.close()
    return get_submission_by_id(sub_id)

def list_all_codes_for_problem(problem_id: str) -> List[str]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT code FROM submissions WHERE problem_id = %s", (problem_id,))
    rows = cursor.fetchall()
    conn.close()
    return [r["code"] for r in rows if r.get("code")]

def delete_submission(sub_id: str) -> bool:
    """
    Xóa vĩnh viễn một bài nộp khỏi CSDL.
    Trả về True nếu xóa thành công, ngược lại False.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM submissions WHERE id = %s", (sub_id,))
    deleted = (cursor.rowcount > 0)
    conn.commit()
    conn.close()
    return deleted

# ========================================================
# CONTEST CRUD FUNCTIONS
# ========================================================
def list_contests() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contests ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for d in rows:
        try:
            d["problems"] = json.loads(d["problems"])
        except Exception:
            d["problems"] = ["CA-101", "CA-102", "CA-103", "CA-104"]
        result.append(d)
    return result

def get_contest_by_id(contest_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contests WHERE id = %s", (contest_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    try:
        row["problems"] = json.loads(row["problems"])
    except Exception:
        row["problems"] = ["CA-101", "CA-102", "CA-103", "CA-104"]
    return row

def create_contest(contest_data: dict) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    contest_id = contest_data.get("id") or f"CONTEST-{int(datetime.now().timestamp()) % 100000:05d}"
    problems_json = json.dumps(contest_data.get("problems", ["CA-101", "CA-102", "CA-103", "CA-104"]))

    cursor.execute("""
    INSERT INTO contests (
        id, title, `desc`, creator, start_time, duration_minutes, status, rule, grader_mode, problems, created_at
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        contest_id,
        contest_data["title"],
        contest_data.get("desc", ""),
        contest_data.get("creator", "TS. Nguyễn Thị Hoa Huệ"),
        now,
        contest_data.get("duration_minutes", 120),
        "Đang diễn ra",
        contest_data.get("rule", "Luật ICPC (Penalty 20 phút/lần nộp sai)"),
        contest_data.get("grader_mode", "hybrid"),
        problems_json,
        now
    ))
    conn.commit()
    conn.close()
    return get_contest_by_id(contest_id)

def cancel_contest(contest_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE contests SET status = 'Đã hủy' WHERE id = %s", (contest_id,))
    conn.commit()
    conn.close()
    return get_contest_by_id(contest_id)
