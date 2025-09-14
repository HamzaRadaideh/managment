# app/web/web_routers.py
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.schemas.models.users_models import User
from app.utility.auth import get_current_user
from app.api.services.tasks_services import TaskService, get_task_service
from app.api.services.notes_services import NoteService, get_note_service
from app.api.services.collections_services import CollectionService, get_collection_service
from app.api.services.tags_services import TagService, get_tag_service
from app.api.services.search_services import SearchService, get_search_service

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

router = APIRouter(tags=["web"])

# Helper function to get current user for web routes (optional, doesn't redirect)
async def get_current_user_optional(request: Request) -> Optional[User]:
    """Get current user without redirecting if not authenticated"""
    try:
        # Extract token from cookies or header
        token = request.cookies.get("auth_token") or request.headers.get("authorization", "").replace("Bearer ", "")
        if not token:
            return None
        
        # You'll need to implement token validation here
        # This is a simplified version - you should use proper dependency injection
        from app.utility.auth import get_current_user
        from app.schemas.database import get_async_session
        
        # This is a workaround - in practice, you'd want to properly inject dependencies
        return None  # Placeholder - implement proper user retrieval
    except:
        return None

# Public routes (no auth required)
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return request.app.state.templates.TemplateResponse(
        "index.html", {"request": request}
    )

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "login.html", {"request": request}
    )

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("register.html", {"request": request})

# Protected routes (auth required)
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Dashboard page"""
    return templates.TemplateResponse(
        "dashboard/index.html", 
        {"request": request, "user": current_user}
    )

@router.get("/tasks", response_class=HTMLResponse)
async def tasks_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
    collection_service: CollectionService = Depends(get_collection_service),
    tag_service: TagService = Depends(get_tag_service),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    collection_id: Optional[int] = None,
):
    """Tasks listing page"""
    tasks = await task_service.get_user_tasks(
        current_user.id, status=status, priority=priority, collection_id=collection_id
    )
    collections = await collection_service.get_user_collections(current_user.id)
    tags = await tag_service.get_user_tags(current_user.id)
    
    return templates.TemplateResponse(
        "tasks/index.html",
        {
            "request": request,
            "user": current_user,
            "tasks": tasks,
            "collections": collections,
            "tags": tags,
            "current_status": status,
            "current_priority": priority,
            "current_collection_id": collection_id,
        }
    )

@router.get("/tasks/{task_id}", response_class=HTMLResponse)
async def task_detail(
    request: Request,
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Task detail page"""
    try:
        task = await task_service.get_user_task_by_id(current_user.id, task_id)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return templates.TemplateResponse(
        "tasks/detail.html",
        {"request": request, "user": current_user, "task": task}
    )

@router.get("/notes", response_class=HTMLResponse)
async def notes_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
    collection_service: CollectionService = Depends(get_collection_service),
    tag_service: TagService = Depends(get_tag_service),
    collection_id: Optional[int] = None,
):
    """Notes listing page"""
    notes = await note_service.get_user_notes(current_user.id, collection_id=collection_id)
    collections = await collection_service.get_user_collections(current_user.id)
    tags = await tag_service.get_user_tags(current_user.id)
    
    return templates.TemplateResponse(
        "notes/index.html",
        {
            "request": request,
            "user": current_user,
            "notes": notes,
            "collections": collections,
            "tags": tags,
            "current_collection_id": collection_id,
        }
    )

@router.get("/notes/{note_id}", response_class=HTMLResponse)
async def note_detail(
    request: Request,
    note_id: int,
    current_user: User = Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
):
    """Note detail page"""
    try:
        note = await note_service.get_user_note_by_id(current_user.id, note_id)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return templates.TemplateResponse(
        "notes/detail.html",
        {"request": request, "user": current_user, "note": note}
    )

@router.get("/collections", response_class=HTMLResponse)
async def collections_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    collection_service: CollectionService = Depends(get_collection_service),
    tag_service: TagService = Depends(get_tag_service),
    type: Optional[str] = None,
):
    """Collections listing page"""
    collections = await collection_service.get_user_collections(current_user.id, type_filter=type)
    tags = await tag_service.get_user_tags(current_user.id)
    
    return templates.TemplateResponse(
        "collections/index.html",
        {
            "request": request,
            "user": current_user,
            "collections": collections,
            "tags": tags,
            "current_type": type,
        }
    )

@router.get("/collections/{collection_id}", response_class=HTMLResponse)
async def collection_detail(
    request: Request,
    collection_id: int,
    current_user: User = Depends(get_current_user),
    collection_service: CollectionService = Depends(get_collection_service),
):
    """Collection detail page"""
    try:
        collection = await collection_service.get_user_collection_by_id(
            current_user.id, collection_id, preload_items=True
        )
    except HTTPException:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    return templates.TemplateResponse(
        "collections/detail.html",
        {"request": request, "user": current_user, "collection": collection}
    )

@router.get("/tags", response_class=HTMLResponse)
async def tags_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    tag_service: TagService = Depends(get_tag_service),
):
    """Tags listing page"""
    tags = await tag_service.get_user_tags(current_user.id)
    
    return templates.TemplateResponse(
        "tags/index.html",
        {"request": request, "user": current_user, "tags": tags}
    )

@router.get("/search", response_class=HTMLResponse)
async def search_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service),
    q: Optional[str] = None,
):
    """Search results page"""
    results = None
    
    if q and len(q.strip()) >= 2:
        try:
            results = await search_service.global_search(
                user_id=current_user.id,
                query=q.strip(),
                limit_per_type=20
            )
        except HTTPException:
            pass  # Handle search errors gracefully
    
    return templates.TemplateResponse(
        "search/results.html",
        {
            "request": request,
            "user": current_user,
            "query": q,
            "results": results,
        }
    )

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """User profile page"""
    return templates.TemplateResponse(
        "profile/index.html",
        {"request": request, "user": current_user}
    )