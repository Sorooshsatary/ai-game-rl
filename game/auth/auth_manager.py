"""Authentication and Role-Based Access Control (RBAC)."""

from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends
from game.database.db import get_user_from_session


def extract_token_from_request(request: Request) -> Optional[str]:
    # 1. Check Authorization header: Bearer <token>
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    # 2. Check X-Session-Token header
    session_header = request.headers.get("X-Session-Token")
    if session_header:
        return session_header.strip()

    # 3. Check cookies
    cookie_token = request.cookies.get("session_token")
    if cookie_token:
        return cookie_token.strip()

    return None


async def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    token = extract_token_from_request(request)
    if not token:
        return None
    return get_user_from_session(token)


async def require_authenticated_user(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)) -> Dict[str, Any]:
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="برای دسترسی به این بخش، لطفاً ابتدا وارد حساب کاربری خود شوید."
        )
    return current_user


async def require_admin(current_user: Dict[str, Any] = Depends(require_authenticated_user)) -> Dict[str, Any]:
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="دسترسی غیرمجاز: تنها کاربران با سطح دسترسی مدیر مجاز به انجام این عملیات هستند."
        )
    return current_user
