import os
from pathlib import Path

# Thư mục gốc dự án
BASE_DIR = Path(__file__).resolve().parent.parent

# Tự động nạp file .env nếu có mà không cần thư viện bên thứ 3
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v
    except Exception as e:
        print(f"[CodeArena Config] Cảnh báo đọc file .env: {e}")

# Cấu hình Cơ sở dữ liệu: Hỗ trợ PostgreSQL (Render / Supabase / Neon) và SQLite (Local Fallback)
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SQLITE_PATH = str(BASE_DIR / "codearena.db")
DB_PATH = SQLITE_PATH

# Cấu hình máy chủ FastAPI
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Cấu hình Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

def get_database_config():
    """Trả về từ điển tóm tắt cấu hình CSDL hiện hành"""
    if DATABASE_URL:
        return {
            "engine": "PostgreSQL",
            "connected": True,
            "url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "configured"
        }
    return {
        "engine": "SQLite",
        "connected": True,
        "path": SQLITE_PATH
    }

def get_ai_config():
    """Trả về trạng thái hoạt động của mô hình AI đánh giá mã nguồn"""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    return {
        "provider": "Google Gemini 1.5 Flash" if api_key else "AST Heuristic Engine",
        "is_ai_real": bool(api_key),
        "model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip(),
        "status": "Online (Gemini Cloud API)" if api_key else "Offline (AST Static Analyzer)"
    }

def save_gemini_key(key: str) -> bool:
    """Lưu API Key vào môi trường runtime và file .env"""
    os.environ["GEMINI_API_KEY"] = key.strip()
    try:
        env_content = ""
        if ENV_FILE.exists():
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                env_content = f.read()
        if "GEMINI_API_KEY=" in env_content:
            new_lines = []
            for line in env_content.splitlines():
                if line.strip().startswith("GEMINI_API_KEY="):
                    new_lines.append(f"GEMINI_API_KEY={key.strip()}")
                else:
                    new_lines.append(line)
            with open(ENV_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines) + "\n")
        else:
            with open(ENV_FILE, "a", encoding="utf-8") as f:
                f.write(f"\nGEMINI_API_KEY={key.strip()}\n")
        return True
    except Exception as e:
        print(f"[CodeArena Config] Lỗi ghi .env: {e}")
        return False
