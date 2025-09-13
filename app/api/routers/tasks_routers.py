# app/api/routers/tasks_routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.contracts.tasks_dtos import TaskCreate, TaskOut, TaskBase
from app.schemas.models.users_models import User
from app.schemas.database import get_async_session
from app.utility.auth import get_current_user
from app.api.repositories.tasks_repositories import get_task_repository
from app.api.services.tasks_services import get_task_service
from app.api.repositories.tasks_repositories import TaskRepository
from app.api.services.tasks_services import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=List[TaskOut])
async def list_tasks(
    status: str = None,
    priority: str = None,
    collection_id: int = None,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
    task_repo: TaskRepository = Depends(get_task_repository),
    db: AsyncSession = Depends(get_async_session)
):
    task_service.task_repo = task_repo # Inject repo
    return await task_service.get_user_tasks(
        current_user.id, status, priority, collection_id
    )

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
    task_repo: TaskRepository = Depends(get_task_repository),
    db: AsyncSession = Depends(get_async_session)
):
    task_service.task_repo = task_repo
    return await task_service.get_user_task_by_id(current_user.id, task_id)

@router.post("/", response_model=TaskOut, status_code=201)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
    task_repo: TaskRepository = Depends(get_task_repository),
    db: AsyncSession = Depends(get_async_session)
):
    task_service.task_repo = task_repo
    return await task_service.create_task_for_user(current_user.id, task)

@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    task_update: TaskBase,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
    task_repo: TaskRepository = Depends(get_task_repository),
    db: AsyncSession = Depends(get_async_session)
):
    task_service.task_repo = task_repo
    return await task_service.update_user_task(
        current_user.id, task_id, task_update
    )

@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
    task_repo: TaskRepository = Depends(get_task_repository),
    db: AsyncSession = Depends(get_async_session)
):
    task_service.task_repo = task_repo
    await task_service.delete_user_task(current_user.id, task_id)
    return 

