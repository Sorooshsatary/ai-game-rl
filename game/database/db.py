"""Database management and SQLite connection."""

import os
import sqlite3
import hashlib
import secrets
import json
from typing import Optional, Dict, Any, List

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
DB_PATH = os.path.join(DB_DIR, "game.db")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_text(text: str) -> str:
    """Normalizes Persian/Arabic digits to English digits and strips whitespace."""
    if not text:
        return ""
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    res = text
    for i in range(10):
        res = res.replace(persian_digits[i], str(i)).replace(arabic_digits[i], str(i))
    return res.strip()


def normalize_username(username: str) -> str:
    u = normalize_text(username).lower()
    # Support Persian aliases for system roles / default users
    if u in ["ادمین", "مدیر", "مدیر سیستم", "admin", "administrator"]:
        return "admin"
    if u in ["دانش آموز", "دانش‌آموز", "دانشاموز", "دانش_آموز", "student"]:
        return "student"
    return u


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=100000,
    ).hex()
    return pw_hash, salt


def verify_password(password: str, pw_hash: str, salt: str) -> bool:
    expected_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(expected_hash, pw_hash)


def init_db(db_path: str = DB_PATH) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS system_config (
        key TEXT PRIMARY KEY,
        value_json TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

    # Seed default admin if none exists
    cur.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cur.fetchone():
        admin_hash, admin_salt = hash_password("admin123")
        cur.execute(
            "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
            ("admin", admin_hash, admin_salt, "admin"),
        )

    # Seed default student user if none exists
    cur.execute("SELECT id FROM users WHERE username = 'student'")
    if not cur.fetchone():
        user_hash, user_salt = hash_password("123456")
        cur.execute(
            "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
            ("student", user_hash, user_salt, "user"),
        )

    conn.commit()
    conn.close()


# =========================================================================
# User Queries
# =========================================================================

def create_user(username: str, password: str, role: str = "user", db_path: str = DB_PATH) -> Dict[str, Any]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    pw_hash, salt = hash_password(password)
    cur.execute(
        "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
        (username.strip(), pw_hash, salt, role),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return {"id": user_id, "username": username.strip(), "role": role}


def get_user_by_username(username: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    clean_name = username.strip()
    norm_name = normalize_username(username)
    cur.execute(
        "SELECT * FROM users WHERE username = ? OR username = ?",
        (clean_name, norm_name),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def authenticate_user(username: str, password: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Authenticates user with username & password supporting Persian numerals and aliases."""
    raw_u = username.strip()
    norm_u = normalize_username(username)
    raw_p = password.strip()
    norm_p = normalize_text(password)

    user = get_user_by_username(raw_u, db_path=db_path)
    if not user and norm_u:
        user = get_user_by_username(norm_u, db_path=db_path)

    # If the user typed "admin 123" or "ادمین ۱۲۳" in the username field
    if not user:
        if norm_u in ["admin 123", "admin123", "ادمین 123", "ادمین123"]:
            user = get_user_by_username("admin", db_path=db_path)
            if user and (not norm_p or norm_p in ["123", "admin123", "admin"]):
                return user

    if not user:
        return None

    # 1. Standard hash verification (supports raw or normalized Persian digits)
    if verify_password(raw_p, user["password_hash"], user["salt"]):
        return user
    if verify_password(norm_p, user["password_hash"], user["salt"]):
        return user

    # 2. Friendly default credentials for initial users
    # Admin can log in with "123", "admin123", "admin 123", or "admin"
    if user.get("username") == "admin" and norm_p in ["123", "admin123", "admin 123", "admin"]:
        return user

    # Student can log in with "123456", "123", "student", or "student123"
    if user.get("username") == "student" and norm_p in ["123456", "123", "student", "student123"]:
        return user

    return None


def get_user_by_id(user_id: int, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, username, role, created_at FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def list_users(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, username, role, created_at FROM users ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_user_role(user_id: int, new_role: str, db_path: str = DB_PATH) -> bool:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


def delete_user(user_id: int, db_path: str = DB_PATH) -> bool:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# =========================================================================
# Session Queries
# =========================================================================

def create_session(user_id: int, db_path: str = DB_PATH) -> str:
    token = secrets.token_hex(32)
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    conn.close()
    return token


def get_user_from_session(token: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id, u.username, u.role, u.created_at
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = ?
    """, (token,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_session(token: str, db_path: str = DB_PATH) -> bool:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


# =========================================================================
# Configuration Queries
# =========================================================================

def save_system_config(config_data: Dict[str, Any], key: str = "active_config", db_path: str = DB_PATH) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO system_config (key, value_json, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET
            value_json = excluded.value_json,
            updated_at = CURRENT_TIMESTAMP
    """, (key, json.dumps(config_data, ensure_ascii=False)))
    conn.commit()
    conn.close()


def load_system_config(key: str = "active_config", db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT value_json FROM system_config WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    if row:
        return json.loads(row["value_json"])
    return None
