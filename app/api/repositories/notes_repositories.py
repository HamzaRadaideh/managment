# app/api/repositories/notes_repositories.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Sequence
from app.schemas.database import get_async_session
from app.schemas.models.notes_models import Note
from app.schemas.models.collections_models import Collection
from app.schemas.models.tags_models import Tag

class NoteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_notes_by_user(self, user_id: int, collection_id: Optional[int] = None) -> Sequence[Note]:
        stmt = select(Note).where(Note.user_id == user_id)
        if collection_id:
            stmt = stmt.where(Note.collection_id == collection_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_note_by_id(self, note_id: int) -> Note | None:
        return await self.db.get(Note, note_id)

    async def get_note_by_id_and_user(self, note_id: int, user_id: int) -> Note | None:
        result = await self.db.execute(
            select(Note).where(Note.id == note_id, Note.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_note(self, note_data: dict) -> Note:
        db_note = Note(**note_data)
        self.db.add(db_note)
        await self.db.commit()
        await self.db.refresh(db_note)
        return db_note

    async def update_note(self, note: Note, update_data: dict):
        for key, value in update_data.items():
            setattr(note, key, value)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def delete_note(self, note: Note):
        await self.db.delete(note)
        await self.db.commit()

    async def get_collection_by_id_and_user(self, collection_id: int, user_id: int) -> Collection | None:
         result = await self.db.execute(
            select(Collection).where(Collection.id == collection_id, Collection.user_id == user_id)
        )
         return result.scalar_one_or_none()

    async def get_tags_by_ids_and_user(self, tag_ids: list[int], user_id: int) -> Sequence[Tag]:
        """Fetch tags by IDs ensuring they belong to the user."""
        if not tag_ids:
            return []
        stmt = select(Tag).where(Tag.id.in_(tag_ids), Tag.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def set_note_tags(self, note: Note, tags: Sequence[Tag]):
        """Set the tags for a note, replacing existing ones."""
        note.tags = list(tags)

def get_note_repository(
    db: AsyncSession = Depends(get_async_session)
) -> NoteRepository:
    return NoteRepository(db)

