# app/web/web_routers.py
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.api.services.auths_services import AuthService, get_auth_service
from app.schemas.contracts.users_dtos import UserCreate
from app.utility.auth_web import (
    UserLite,
    create_access_token,
    current_user_optional,
    inject_csrf,
    login_required,
    set_login_cookie,
    clear_login_cookie,
)

router = APIRouter()


def render_template(request: Request, template_name: str, context: dict) -> HTMLResponse:
    """
    Uses the Jinja environment you attached in main.py:
        templates = Jinja2Templates(directory="app/templates")
        app.state.templates = templates
    """
    context = dict(context or {})
    context["request"] = request
    return request.app.state.templates.TemplateResponse(template_name, context)


# ---------- Public Landing ----------
@router.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    user = current_user_optional(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    csrf_token = inject_csrf(request)
    return render_template(
        request,
        "landing.html",
        {"csrf_token": csrf_token, "current_user": None},
    )


# ---------- Web Auth ----------
@router.post("/web/auth/login")
async def web_login(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    username: str = Form(...),
    password: str = Form(...),
):
    # CSRF: allow header (XHR) OR hidden input token from the form
    form = await request.form()
    header_token = request.headers.get("X-CSRF-Token")
    form_token = form.get("csrf_token")
    if (header_token or form_token) != request.session.get("csrf_token"):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    user = await auth_service.authenticate_user(username, password)
    if not user:
        return RedirectResponse("/?error=Invalid%20credentials", status_code=303)

    # IMPORTANT: sub must be a STRING for python-jose
    token = create_access_token(
        {"user_id": user.id, "sub": str(user.id), "username": user.username}
    )
    resp = RedirectResponse("/dashboard", status_code=303)
    set_login_cookie(resp, token)  # set cookie on the response you return
    return resp


@router.post("/web/auth/register")
async def web_register(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    fname: str = Form(...),
    lname: str = Form(...),
):
    form = await request.form()
    header_token = request.headers.get("X-CSRF-Token")
    form_token = form.get("csrf_token")
    if (header_token or form_token) != request.session.get("csrf_token"):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    dto = UserCreate(
        username=username,
        email=email,
        password=password,
        fname=fname,
        lname=lname,
    )
    user = await auth_service.register_user(dto)

    token = create_access_token(
        {"user_id": user.id, "sub": str(user.id), "username": user.username}
    )
    resp = RedirectResponse("/dashboard", status_code=303)
    set_login_cookie(resp, token)
    return resp


@router.post("/web/logout")
async def web_logout():
    resp = RedirectResponse("/", status_code=303)
    clear_login_cookie(resp)
    return resp


# ---------- Authenticated Pages ----------
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: UserLite = Depends(login_required)):
    csrf_token = inject_csrf(request)
    return render_template(
        request,
        "dashboard.html",
        {"current_user": user, "csrf_token": csrf_token},
    )


@router.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request, user: UserLite = Depends(login_required)):
    csrf_token = inject_csrf(request)
    return render_template(
        request,
        "tasks.html",
        {"current_user": user, "csrf_token": csrf_token},
    )


@router.get("/notes", response_class=HTMLResponse)
async def notes_page(request: Request, user: UserLite = Depends(login_required)):
    csrf_token = inject_csrf(request)
    return render_template(
        request,
        "notes.html",
        {"current_user": user, "csrf_token": csrf_token},
    )


@router.get("/collections", response_class=HTMLResponse)
async def collections_page(request: Request, user: UserLite = Depends(login_required)):
    csrf_token = inject_csrf(request)
    return render_template(
        request,
        "collections.html",
        {"current_user": user, "csrf_token": csrf_token},
    )


@router.get("/tags", response_class=HTMLResponse)
async def tags_page(request: Request, user: UserLite = Depends(login_required)):
    csrf_token = inject_csrf(request)
    return render_template(
        request,
        "tags.html",
        {"current_user": user, "csrf_token": csrf_token},
    )
