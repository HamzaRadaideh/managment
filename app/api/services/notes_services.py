# app/api/services/notes_services.py
from app.api.repositories.notes_repositories import NoteRepository, get_note_repository
from app.schemas.models.notes_models import Note
from app.schemas.contracts.notes_dtos import NoteCreate, NoteBase
from fastapi import Depends, HTTPException, status

class NoteService:
    def __init__(self, note_repo: NoteRepository):
        self.note_repo = note_repo

    async def get_user_notes(self, user_id: int, collection_id: int | None = None) -> list[Note]:
        return await self.note_repo.get_notes_by_user(user_id, collection_id)

    async def get_user_note_by_id(self, user_id: int, note_id: int) -> Note:
        note = await self.note_repo.get_note_by_id_and_user(note_id, user_id)
        if not note:
             raise HTTPException(status_code=404, detail="Note not found")
        return note

    async def create_note_for_user(self, user_id: int, note_create: NoteCreate) -> Note:
        note_data = note_create.dict()
        note_data['user_id'] = user_id

        if note_create.collection_id:
            collection = await self.note_repo.get_collection_by_id_and_user(note_create.collection_id, user_id)
            if not collection:
                raise HTTPException(status_code=404, detail="Collection not found or not owned by user")

        return await self.note_repo.create_note(note_data)

    async def update_user_note(self, user_id: int, note_id: int, note_update: NoteBase) -> Note:
        note = await self.get_user_note_by_id(user_id, note_id) # Reuse existing check
        update_data = note_update.dict(exclude_unset=True)
        # Add logic to check collection ownership if collection_id is being updated
        if 'collection_id' in update_data and update_data['collection_id']:
             collection = await self.note_repo.get_collection_by_id_and_user(update_data['collection_id'], user_id)
             if not collection:
                raise HTTPException(status_code=404, detail="Collection not found or not owned by user")
        return await self.note_repo.update_note(note, update_data)

    async def delete_user_note(self, user_id: int, note_id: int):
        note = await self.get_user_note_by_id(user_id, note_id) # Reuse existing check
        await self.note_repo.delete_note(note)

# Dependency
def get_note_service(
    note_repo: NoteRepository = Depends(get_note_repository)
) -> NoteService:
    return NoteService(note_repo)

