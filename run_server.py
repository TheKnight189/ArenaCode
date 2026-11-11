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
    print("=" * 65)
    print("[*] CODEARENA - BACKEND SERVER FASTAPI (PYTHON 3.14)")
    print("=" * 65)
    print(">> Web App:      http://localhost:8000")
    print(">> Swagger Docs: http://localhost:8000/docs")
    print(">> ReDoc Docs:   http://localhost:8000/redoc")
    print(">> Admin Login:  admin@haui.edu.vn / admin")
    print("=" * 65)
    print("Press Ctrl + C to stop server.")
    print()
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

