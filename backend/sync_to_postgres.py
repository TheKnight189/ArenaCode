#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Công cụ đồng bộ dữ liệu CSDL từ SQLite cục bộ (codearena.db) lên PostgreSQL trên Render.com
Sử dụng:
    python backend/sync_to_postgres.py
hoặc:
    python backend/sync_to_postgres.py "postgresql://user:pass@host/dbname"
"""

import sys
import os
import sqlite3
import logging

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.config import DATABASE_URL, SQLITE_PATH
from backend.database import _init_postgres_schema

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("codearena.sync")

def sync_sqlite_to_postgres(target_url: str = None):
    url = target_url or DATABASE_URL
    if not url:
        print("=" * 68)
        print("[-] CHƯA CẤU HÌNH DATABASE_URL CỦA RENDER!")
        print("=" * 68)
        print("Hướng dẫn:")
        print("1. Vào Render Dashboard (https://dashboard.render.com).")
        print("2. Chọn PostgreSQL Database (ví dụ: arenacode-db).")
        print("3. Sao chép 'External Database URL'.")
        print("4. Điền vào file .env:")
        print("   DATABASE_URL=postgresql://user:pass@host.singapore-postgres.render.com/dbname")
        print("   hoặc chạy lệnh:")
        print("   python backend/sync_to_postgres.py \"postgresql://user:pass@host/dbname\"")
        print("=" * 68)
        return False

    if url.startswith("postgres://"):
        url = "postgresql://" + url[11:]

    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        logger.error("Chưa cài đặt thư viện psycopg2. Vui lòng chạy: pip install psycopg2-binary")
        return False

    if not os.path.exists(SQLITE_PATH):
        logger.error(f"Không tìm thấy file CSDL SQLite cục bộ: {SQLITE_PATH}")
        return False

    logger.info(f"[*] Đang kết nối CSDL SQLite cục bộ: {SQLITE_PATH}")
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    logger.info("[*] Đang kết nối tới PostgreSQL trên Render Cloud...")
    try:
        pg_conn = psycopg2.connect(url, cursor_factory=RealDictCursor)
        pg_cursor = pg_conn.cursor()
    except Exception as e:
        logger.error(f"[-] Không thể kết nối tới PostgreSQL: {e}")
        return False

    logger.info("[+] Kết nối PostgreSQL thành công! Bắt đầu khởi tạo schema...")
    _init_postgres_schema(pg_cursor)
    pg_conn.commit()

    tables = ["users", "problems", "contests", "submissions", "system_logs"]
    summary = {}

    for table in tables:
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        if not rows:
            logger.info(f" - Bảng '{table}': 0 bản ghi (bỏ qua)")
            summary[table] = 0
            continue

        columns = [d[0] for d in sqlite_cursor.description]
        escaped_cols = [f'"{col}"' if col in ("desc", "user") else col for col in columns]
        cols_str = ", ".join(escaped_cols)
        placeholders = ", ".join(["%s"] * len(columns))

        # Build ON CONFLICT DO UPDATE
        update_clauses = [
            f'{col} = EXCLUDED.{col}'
            for col in escaped_cols if col != "id"
        ]
        update_str = ", ".join(update_clauses)
        if update_str:
            sql = f"""
            INSERT INTO {table} ({cols_str})
            VALUES ({placeholders})
            ON CONFLICT (id) DO UPDATE SET {update_str};
            """
        else:
            sql = f"""
            INSERT INTO {table} ({cols_str})
            VALUES ({placeholders})
            ON CONFLICT (id) DO NOTHING;
            """

        inserted_count = 0
        for row in rows:
            values = [row[c] for c in columns]
            pg_cursor.execute(sql, values)
            inserted_count += 1

        pg_conn.commit()
        logger.info(f" [✓] Đã đồng bộ bảng '{table}': {inserted_count} bản ghi.")
        summary[table] = inserted_count

    sqlite_conn.close()
    pg_conn.close()

    print("\n" + "=" * 68)
    print("       ĐỒNG BỘ DỮ LIỆU LÊN RENDER POSTGRESQL THÀNH CÔNG!")
    print("=" * 68)
    for t, cnt in summary.items():
        print(f"  - Bảng {t.ljust(15)}: {cnt} bản ghi")
    print("=" * 68)
    print("Bây giờ bạn có thể điền DATABASE_URL vào .env để sử dụng chung CSDL.")
    print("=" * 68 + "\n")
    return True

if __name__ == "__main__":
    cli_url = sys.argv[1] if len(sys.argv) > 1 else None
    sync_sqlite_to_postgres(cli_url)
