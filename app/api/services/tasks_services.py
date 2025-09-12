# app/api/services/tasks_services.py
from app.api.repositories.tasks_repositories import TaskRepository, get_task_repository
from app.schemas.models.tasks_models import Task
from app.schemas.contracts.tasks_dtos import TaskCreate, TaskBase
from fastapi import Depends, HTTPException, status

class TaskService:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def get_user_tasks(
        self, 
        user_id: int, 
        status: str | None = None, 
        priority: str | None = None, 
        collection_id: int | None = None
    ) -> list[Task]:
        return await self.task_repo.get_tasks_by_user(user_id, status, priority, collection_id)

    async def get_user_task_by_id(self, user_id: int, task_id: int) -> Task:
        task = await self.task_repo.get_task_by_id_and_user(task_id, user_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    async def create_task_for_user(self, user_id: int, task_create: TaskCreate) -> Task:
        task_data = task_create.dict()
        task_data['user_id'] = user_id

        if task_create.collection_id:
            collection = await self.task_repo.get_collection_by_id_and_user(
                task_create.collection_id, user_id
            )
            if not collection:
                raise HTTPException(
                    status_code=404, 
                    detail="Collection not found or not owned by user"
                )

        return await self.task_repo.create_task(task_data)

    async def update_user_task(
        self, 
        user_id: int, 
        task_id: int, 
        task_update: TaskBase
    ) -> Task:
        task = await self.get_user_task_by_id(user_id, task_id)
        update_data = task_update.dict(exclude_unset=True)
        
        # Validate collection ownership if collection_id is being updated
        if 'collection_id' in update_data and update_data['collection_id']:
            collection = await self.task_repo.get_collection_by_id_and_user(
                update_data['collection_id'], user_id
            )
            if not collection:
                raise HTTPException(
                    status_code=404, 
                    detail="Collection not found or not owned by user"
                )
                
        return await self.task_repo.update_task(task, update_data)

    async def delete_user_task(self, user_id: int, task_id: int):
        task = await self.get_user_task_by_id(user_id, task_id)
        await self.task_repo.delete_task(task)

# Dependency
def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repository)
) -> TaskService:
    return TaskService(task_repo)

