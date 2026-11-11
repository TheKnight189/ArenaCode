import uvicorn
import sys
import os

# Ensure UTF-8 output on Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add root directory to python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("RELOAD", "false").lower() in ("true", "1") if "PORT" in os.environ else True

    print("=" * 65)
    print("[*] CODEARENA - BACKEND SERVER FASTAPI")
    print("=" * 65)
    print(f">> Web App:      http://localhost:{port}")
    print(f">> Student:      http://localhost:{port}/student")
    print(f">> Teacher:      http://localhost:{port}/teacher")
    print(f">> Admin:        http://localhost:{port}/admin")
    print(f">> Swagger Docs: http://localhost:{port}/docs")
    print(">> Admin Login:  admin@haui.edu.vn / admin")
    print("=" * 65)
    print("Press Ctrl + C to stop server.")
    print()
    uvicorn.run("backend.main:app", host=host, port=port, reload=reload)

