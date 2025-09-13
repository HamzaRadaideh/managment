# app/api/repositories/tasks_repositories.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Sequence
from app.schemas.database import get_async_session
from app.schemas.models.tags_models import Tag
from app.schemas.models.tasks_models import Task
from app.schemas.models.collections_models import Collection

class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tasks_by_user(
        self, 
        user_id: int, 
        status: Optional[str] = None, 
        priority: Optional[str] = None, 
        collection_id: Optional[int] = None
    ) -> Sequence[Task]:
        stmt = select(Task).where(Task.user_id == user_id)
        if status:
            stmt = stmt.where(Task.status == status)
        if priority:
            stmt = stmt.where(Task.priority == priority)
        if collection_id:
            stmt = stmt.where(Task.collection_id == collection_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_task_by_id(self, task_id: int) -> Task | None:
        return await self.db.get(Task, task_id)

    async def get_task_by_id_and_user(self, task_id: int, user_id: int) -> Task | None:
        result = await self.db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_task(self, task_data: dict) -> Task:
        db_task = Task(**task_data)
        self.db.add(db_task)
        await self.db.commit()
        await self.db.refresh(db_task)
        return db_task

    async def update_task(self, task: Task, update_data: dict):
        for key, value in update_data.items():
            setattr(task, key, value)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete_task(self, task: Task):
        await self.db.delete(task)
        await self.db.commit()

    async def get_collection_by_id_and_user(self, collection_id: int, user_id: int) -> Collection | None:
        result = await self.db.execute(
            select(Collection).where(
                Collection.id == collection_id, 
                Collection.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_tags_by_ids_and_user(self, tag_ids: list[int], user_id: int) -> Sequence[Tag]:
        """Fetch tags by IDs ensuring they belong to the user."""
        if not tag_ids:
            return [] # Handle empty list
        stmt = select(Tag).where(Tag.id.in_(tag_ids), Tag.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def set_task_tags(self, task: Task, tags: Sequence[Tag]):
        """Set the tags for a task, replacing existing ones."""
        task.tags = list(tags)

def get_task_repository(
    db: AsyncSession = Depends(get_async_session)
) -> TaskRepository:
    return TaskRepository(db)

