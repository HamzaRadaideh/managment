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
        # Extract tag_ids before creating the task
        tag_ids = task_data.pop('tag_ids', None) # Remove tag_ids from task_data
        task_data['user_id'] = user_id

        # Handle collection ownership check (existing logic)
        if task_create.collection_id:
            collection = await self.task_repo.get_collection_by_id_and_user(
                task_create.collection_id, user_id
            )
            if not collection:
                raise HTTPException(
                    status_code=404,
                    detail="Collection not found or not owned by user"
                )

        # --- Handle tags ---
        associated_tags = []
        if tag_ids is not None: # Check if tag_ids was provided (even if empty list)
             # Validate tag ownership
             associated_tags = await self.task_repo.get_tags_by_ids_and_user(tag_ids, user_id)
             if len(associated_tags) != len(set(tag_ids)): # Check if all IDs were found
                  found_tag_ids = {tag.id for tag in associated_tags}
                  missing_tag_ids = set(tag_ids) - found_tag_ids
                  raise HTTPException(
                      status_code=400,
                      detail=f"Tags not found or not owned by user: {list(missing_tag_ids)}"
                  )

        # Create the task first
        new_task = await self.task_repo.create_task(task_data)

        # Associate tags if any were provided
        if associated_tags:
            await self.task_repo.set_task_tags(new_task, associated_tags)
            await self.task_repo.db.commit() # Commit the tag associations
            await self.task_repo.db.refresh(new_task) # Refresh to load tags relation for output DTO

        return new_task # Return the task (tag_ids will be serialized by Pydantic)

    async def update_user_task(
        self,
        user_id: int,
        task_id: int,
        task_update: TaskBase # Now includes tag_ids
    ) -> Task:
        task = await self.get_user_task_by_id(user_id, task_id)
        update_data = task_update.dict(exclude_unset=True)
        # Extract tag_ids if it's in the update data
        tag_ids_to_set = update_data.pop('tag_ids', None) # Remove from update_data dict

        # Validate collection ownership if collection_id is being updated (existing logic)
        if 'collection_id' in update_data and update_data['collection_id']:
            collection = await self.task_repo.get_collection_by_id_and_user(
                update_data['collection_id'], user_id
            )
            if not collection:
                raise HTTPException(
                    status_code=404,
                    detail="Collection not found or not owned by user"
                )

        # --- Handle tag updates ---
        if tag_ids_to_set is not None: # Check if tag_ids was provided in the update
            if tag_ids_to_set: # If list is not empty, validate and set
                # Validate tag ownership
                associated_tags = await self.task_repo.get_tags_by_ids_and_user(tag_ids_to_set, user_id)
                if len(associated_tags) != len(set(tag_ids_to_set)):
                    found_tag_ids = {tag.id for tag in associated_tags}
                    missing_tag_ids = set(tag_ids_to_set) - found_tag_ids
                    raise HTTPException(
                        status_code=400,
                        detail=f"Tags not found or not owned by user: {list(missing_tag_ids)}"
                    )
                await self.task_repo.set_task_tags(task, associated_tags)
            else: # If empty list was provided, clear tags
                await self.task_repo.set_task_tags(task, [])
            # Commit tag changes immediately
            await self.task_repo.db.commit()
            # Refresh task to ensure tag_ids are loaded for the response DTO
            await self.task_repo.db.refresh(task)

        # Update other task fields (excluding tag_ids now)
        if update_data: # Only proceed if there are other fields to update
            for key, value in update_data.items():
                setattr(task, key, value)
            await self.task_repo.db.commit()
            await self.task_repo.db.refresh(task)

        return task

    async def delete_user_task(self, user_id: int, task_id: int):
        task = await self.get_user_task_by_id(user_id, task_id)
        await self.task_repo.delete_task(task)

# Dependency
def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repository)
) -> TaskService:
    return TaskService(task_repo)

