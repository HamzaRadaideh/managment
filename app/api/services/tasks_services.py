# app/api/services/tasks_services.py
from fastapi import Depends, HTTPException, status

from app.api.repositories.tasks_repositories import (
    TaskRepository,
    get_task_repository,
)
from app.schemas.models.tasks_models import Task
from app.schemas.contracts.tasks_dtos import TaskCreate, TaskBase


class TaskService:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def get_user_tasks(
        self,
        user_id: int,
        status: str | None = None,
        priority: str | None = None,
        collection_id: int | None = None,
    ) -> list[Task]:
        return await self.task_repo.get_tasks_by_user(
            user_id=user_id,
            status=status,
            priority=priority,
            collection_id=collection_id,
        )

    async def get_user_task_by_id(self, user_id: int, task_id: int) -> Task:
        task = await self.task_repo.get_task_by_id_and_user(task_id, user_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    async def create_task_for_user(self, user_id: int, task_create: TaskCreate) -> Task:
        data = task_create.dict()
        tag_ids = data.pop("tag_ids", None)
        data["user_id"] = user_id

        # Validate collection ownership if provided
        if task_create.collection_id:
            owned = await self.task_repo.get_collection_by_id_and_user(
                task_create.collection_id, user_id
            )
            if not owned:
                raise HTTPException(
                    status_code=404, detail="Collection not found or not owned by user"
                )

        # Validate tags if provided
        if tag_ids is not None:
            found = await self.task_repo.get_tags_by_ids_and_user(tag_ids, user_id)
            if len(found) != len(set(tag_ids)):
                found_ids = {t.id for t in found}
                missing = sorted(set(tag_ids) - found_ids)
                raise HTTPException(
                    status_code=400,
                    detail=f"Tags not found or not owned by user: {missing}",
                )

        # Create & set tags
        new_task = await self.task_repo.create_task(data)
        if tag_ids is not None:
            await self.task_repo.set_task_tags(new_task, tag_ids)

        # One commit, then FULL refresh, then targeted refresh for tags
        await self.task_repo.db.commit()
        await self.task_repo.db.refresh(new_task)                       # full refresh (timestamps, etc.)
        await self.task_repo.db.refresh(new_task, attribute_names=["tags"])  # ensure tags loaded for tag_ids property
        return new_task

    async def update_user_task(
        self, user_id: int, task_id: int, task_update: TaskBase
    ) -> Task:
        task = await self.get_user_task_by_id(user_id, task_id)

        update_data = task_update.dict(exclude_unset=True)
        tag_ids_to_set = update_data.pop("tag_ids", None)

        # Validate collection if changed
        if "collection_id" in update_data and update_data["collection_id"]:
            owned = await self.task_repo.get_collection_by_id_and_user(
                update_data["collection_id"], user_id
            )
            if not owned:
                raise HTTPException(
                    status_code=404, detail="Collection not found or not owned by user"
                )

        # Validate tags if provided
        if tag_ids_to_set is not None:
            found = await self.task_repo.get_tags_by_ids_and_user(tag_ids_to_set, user_id)
            if len(found) != len(set(tag_ids_to_set)):
                found_ids = {t.id for t in found}
                missing = sorted(set(tag_ids_to_set) - found_ids)
                raise HTTPException(
                    status_code=400,
                    detail=f"Tags not found or not owned by user: {missing}",
                )

        # Apply changes
        if update_data:
            await self.task_repo.update_task(task, update_data)
        if tag_ids_to_set is not None:
            await self.task_repo.set_task_tags(task, tag_ids_to_set)

        # Commit once, then FULL refresh + tags refresh (prevents MissingGreenlet on updated_at/tag_ids)
        await self.task_repo.db.commit()
        await self.task_repo.db.refresh(task)                            # full
        await self.task_repo.db.refresh(task, attribute_names=["tags"])  # tags
        return task


def get_task_service(task_repo: TaskRepository = Depends(get_task_repository)) -> TaskService:
    return TaskService(task_repo)

