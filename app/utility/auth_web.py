# app/utility/auth_web.py
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, TypedDict

from fastapi import HTTPException, Request, Response, status
from jose import JWTError, jwt

# Reuse the same key/alg that your API uses
from app.utility.auth import SECRET_KEY, ALGORITHM


# -------- Config --------
ACCESS_TTL_MINUTES = 60 * 24 * 7  # 7 days
COOKIE_NAME = "access_token"
CSRF_HEADER = "X-CSRF-Token"


# -------- Typed user for templates --------
class UserLite(TypedDict):
    id: int
    username: str


# -------- JWT helpers --------
def create_access_token(payload: dict, minutes: int = ACCESS_TTL_MINUTES) -> str:
    """
    Create a JWT. Ensures `sub` is a string (python-jose requirement).
    """
    to_encode = payload.copy()
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _decode(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# -------- Cookie helpers --------
def set_login_cookie(resp: Response, token: str) -> None:
    """
    Set the HttpOnly auth cookie. Secure=False for local dev; set True behind HTTPS.
    """
    resp.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # flip to True in production (HTTPS)
        path="/",
        max_age=ACCESS_TTL_MINUTES * 60,
    )


def clear_login_cookie(resp: Response) -> None:
    resp.delete_cookie(COOKIE_NAME, path="/")


# -------- CSRF helpers (double-submit using session) --------
def inject_csrf(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token


def ensure_csrf(request: Request) -> None:
    """
    For XHR calls: require the CSRF header to match the session token.
    (Form posts can pass a hidden input; see web_routers for that path.)
    """
    session_token = request.session.get("csrf_token")
    header_token = request.headers.get(CSRF_HEADER)
    if not session_token or not header_token or header_token != session_token:
        raise HTTPException(status_code=403, detail="Invalid or missing CSRF token")


# -------- Current-user helpers for web templates --------
def _payload_to_user(payload: dict) -> Optional[UserLite]:
    uid = payload.get("user_id") or payload.get("sub")
    if not uid:
        return None
    return UserLite(id=int(uid), username=payload.get("username", ""))


def current_user_optional(request: Request) -> Optional[UserLite]:
    # 1) Cookie
    ctoken = request.cookies.get(COOKIE_NAME)
    if ctoken:
        payload = _decode(ctoken)
        if payload:
            user = _payload_to_user(payload)
            if user:
                return user
    # 2) Bearer (optional fallback)
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        payload = _decode(auth.split(" ", 1)[1])
        if payload:
            user = _payload_to_user(payload)
            if user:
                return user
    return None


def login_required(request: Request) -> UserLite:
    user = current_user_optional(request)
    if not user:
        # 303 => browser performs GET on "/"
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/"},
        )
    return user
