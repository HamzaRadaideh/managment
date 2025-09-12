# app/api/services/collections_services.py
from app.api.repositories.collections_repositories import CollectionRepository, get_collection_repository
from app.schemas.models.collections_models import Collection
from app.schemas.contracts.collections_dtos import CollectionCreate
from fastapi import Depends, HTTPException, status

class CollectionService:
    def __init__(self, collection_repo: CollectionRepository):
        self.collection_repo = collection_repo

    async def get_user_collections(
        self, 
        user_id: int, 
        type_filter: str | None = None
    ) -> list[Collection]:
        return await self.collection_repo.get_collections_by_user(user_id, type_filter)

    async def get_user_collection_by_id(
        self, 
        user_id: int, 
        collection_id: int, 
        preload_items: bool = False
    ) -> Collection:
        collection = await self.collection_repo.get_collection_by_id_and_user(
            collection_id, user_id
        )
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
            
        if preload_items:
            await self.collection_repo.preload_collection_items(collection)
            
        return collection

    async def create_collection_for_user(
        self, 
        user_id: int, 
        collection_create: CollectionCreate
    ) -> Collection:
        # Prevent duplicate collection titles per user
        existing_collection = await self.collection_repo.get_collection_by_title_and_user(
            collection_create.title, user_id
        )
        if existing_collection:
            raise HTTPException(
                status_code=400, 
                detail="Collection with this title already exists for the user"
            )
            
        collection_data = collection_create.dict()
        collection_data['user_id'] = user_id
        return await self.collection_repo.create_collection(collection_data)

    async def update_user_collection(
        self, 
        user_id: int, 
        collection_id: int, 
        collection_update: CollectionCreate
    ) -> Collection:
        # Ensure the collection exists and belongs to the user
        collection = await self.get_user_collection_by_id(user_id, collection_id)
        
        # Check for duplicate title (excluding the current collection)
        if collection_update.title != collection.title:
            existing_collection = await self.collection_repo.get_collection_by_title_and_user(
                collection_update.title, user_id
            )
            if existing_collection:
                raise HTTPException(
                    status_code=400, 
                    detail="Collection with this title already exists for the user"
                )
                
        update_data = collection_update.dict(exclude_unset=True)
        return await self.collection_repo.update_collection(collection, update_data)

    async def delete_user_collection(self, user_id: int, collection_id: int):
        collection = await self.get_user_collection_by_id(user_id, collection_id)
        await self.collection_repo.delete_collection(collection)

# Dependency
def get_collection_service(
    collection_repo: CollectionRepository = Depends(get_collection_repository)
) -> CollectionService:
    return CollectionService(collection_repo)

