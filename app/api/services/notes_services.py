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
        tag_ids = note_data.pop('tag_ids', None) # Extract tag_ids
        note_data['user_id'] = user_id

        if note_create.collection_id:
            collection = await self.note_repo.get_collection_by_id_and_user(note_create.collection_id, user_id)
            if not collection:
                raise HTTPException(status_code=404, detail="Collection not found or not owned by user")

        associated_tags = []
        if tag_ids is not None:
            associated_tags = await self.note_repo.get_tags_by_ids_and_user(tag_ids, user_id)
            if len(associated_tags) != len(set(tag_ids)):
                found_tag_ids = {tag.id for tag in associated_tags}
                missing_tag_ids = set(tag_ids) - found_tag_ids
                raise HTTPException(
                    status_code=400,
                    detail=f"Tags not found or not owned by user: {list(missing_tag_ids)}"
                )

        new_note = await self.note_repo.create_note(note_data)

        if associated_tags:
            await self.note_repo.set_note_tags(new_note, associated_tags)
            await self.note_repo.db.commit()
            await self.note_repo.db.refresh(new_note)

        return new_note

    async def update_user_note(self, user_id: int, note_id: int, note_update: NoteBase) -> Note:
        note = await self.get_user_note_by_id(user_id, note_id)
        update_data = note_update.dict(exclude_unset=True)
        tag_ids_to_set = update_data.pop('tag_ids', None)

        if 'collection_id' in update_data and update_data['collection_id']:
            collection = await self.note_repo.get_collection_by_id_and_user(update_data['collection_id'], user_id)
            if not collection:
                raise HTTPException(status_code=404, detail="Collection not found or not owned by user")

        if tag_ids_to_set is not None:
            if tag_ids_to_set:
                associated_tags = await self.note_repo.get_tags_by_ids_and_user(tag_ids_to_set, user_id)
                if len(associated_tags) != len(set(tag_ids_to_set)):
                    found_tag_ids = {tag.id for tag in associated_tags}
                    missing_tag_ids = set(tag_ids_to_set) - found_tag_ids
                    raise HTTPException(
                        status_code=400,
                        detail=f"Tags not found or not owned by user: {list(missing_tag_ids)}"
                    )
                await self.note_repo.set_note_tags(note, associated_tags)
            else:
                await self.note_repo.set_note_tags(note, [])
            await self.note_repo.db.commit()
            await self.note_repo.db.refresh(note)

        if update_data:
            for key, value in update_data.items():
                setattr(note, key, value)
            await self.note_repo.db.commit()
            await self.note_repo.db.refresh(note)

        return note

    async def delete_user_note(self, user_id: int, note_id: int):
        note = await self.get_user_note_by_id(user_id, note_id)
        await self.note_repo.delete_note(note)

def get_note_service(
    note_repo: NoteRepository = Depends(get_note_repository)
) -> NoteService:
    return NoteService(note_repo)

