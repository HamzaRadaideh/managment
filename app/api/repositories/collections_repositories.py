# app/api/repositories/collections_repositories.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Sequence
from app.schemas.database import get_async_session
from app.schemas.models.collections_models import Collection
from app.schemas.models.tags_models import Tag

class CollectionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_collections_by_user(
        self, 
        user_id: int, 
        type_filter: Optional[str] = None
    ) -> Sequence[Collection]:
        stmt = select(Collection).where(Collection.user_id == user_id)
        if type_filter:
            stmt = stmt.where(Collection.type == type_filter)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_collection_by_id(self, collection_id: int) -> Collection | None:
        return await self.db.get(Collection, collection_id)

    async def get_collection_by_id_and_user(
        self, 
        collection_id: int, 
        user_id: int
    ) -> Collection | None:
        result = await self.db.execute(
            select(Collection).where(
                Collection.id == collection_id, 
                Collection.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_collection_by_title_and_user(
        self, 
        title: str, 
        user_id: int
    ) -> Collection | None:
        result = await self.db.execute(
            select(Collection).where(
                Collection.title == title, 
                Collection.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def create_collection(self, collection_data: dict) -> Collection:
        db_collection = Collection(**collection_data)
        self.db.add(db_collection)
        await self.db.commit()
        await self.db.refresh(db_collection)
        return db_collection

    async def update_collection(self, collection: Collection, update_data: dict):
        for key, value in update_data.items():
            setattr(collection, key, value)
        await self.db.commit()
        await self.db.refresh(collection)
        return collection

    async def delete_collection(self, collection: Collection):
        await self.db.delete(collection)
        await self.db.commit()

    async def preload_collection_items(self, collection: Collection):
        await self.db.refresh(collection, attribute_names=['tasks', 'notes'])

    async def get_tags_by_ids_and_user(self, tag_ids: list[int], user_id: int) -> Sequence[Tag]:
        """Fetch tags by IDs ensuring they belong to the user."""
        if not tag_ids:
            return []
        stmt = select(Tag).where(Tag.id.in_(tag_ids), Tag.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def set_collection_tags(self, collection: Collection, tags: Sequence[Tag]):
        """Set the tags for a collection, replacing existing ones."""
        collection.tags = list(tags)

def get_collection_repository(
    db: AsyncSession = Depends(get_async_session)
) -> CollectionRepository:
    return CollectionRepository(db)

