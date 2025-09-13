# app/api/services/notes_services.py
from fastapi import Depends, HTTPException, status

from app.api.repositories.notes_repositories import (
    NoteRepository,
    get_note_repository,
)
from app.schemas.models.notes_models import Note
from app.schemas.contracts.notes_dtos import NoteCreate, NoteBase


class NoteService:
    def __init__(self, note_repo: NoteRepository):
        self.note_repo = note_repo

    async def get_user_notes(
        self, user_id: int, collection_id: int | None = None
    ) -> list[Note]:
        return await self.note_repo.get_notes_by_user(user_id=user_id, collection_id=collection_id)

    async def get_user_note_by_id(self, user_id: int, note_id: int) -> Note:
        note = await self.note_repo.get_note_by_id_and_user(note_id, user_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note

    async def create_note_for_user(self, user_id: int, note_create: NoteCreate) -> Note:
        data = note_create.dict()
        tag_ids = data.pop("tag_ids", None)
        data["user_id"] = user_id

        # Validate collection if provided
        if note_create.collection_id:
            owned = await self.note_repo.get_collection_by_id_and_user(note_create.collection_id, user_id)
            if not owned:
                raise HTTPException(
                    status_code=404, detail="Collection not found or not owned by user"
                )

        # Validate tags if provided
        if tag_ids is not None:
            found = await self.note_repo.get_tags_by_ids_and_user(tag_ids, user_id)
            if len(found) != len(set(tag_ids)):
                found_ids = {t.id for t in found}
                missing = sorted(set(tag_ids) - found_ids)
                raise HTTPException(
                    status_code=400,
                    detail=f"Tags not found or not owned by user: {missing}",
                )

        new_note = await self.note_repo.create_note(data)
        if tag_ids is not None:
            await self.note_repo.set_note_tags(new_note, tag_ids)

        await self.note_repo.db.commit()
        await self.note_repo.db.refresh(new_note)                         # full
        await self.note_repo.db.refresh(new_note, attribute_names=["tags"])
        return new_note

    async def update_user_note(
        self, user_id: int, note_id: int, note_update: NoteBase
    ) -> Note:
        note = await self.get_user_note_by_id(user_id, note_id)

        update_data = note_update.dict(exclude_unset=True)
        tag_ids_to_set = update_data.pop("tag_ids", None)

        # Validate collection if changed
        if "collection_id" in update_data and update_data["collection_id"]:
            owned = await self.note_repo.get_collection_by_id_and_user(update_data["collection_id"], user_id)
            if not owned:
                raise HTTPException(
                    status_code=404, detail="Collection not found or not owned by user"
                )

        # Validate tags if provided
        if tag_ids_to_set is not None:
            found = await self.note_repo.get_tags_by_ids_and_user(tag_ids_to_set, user_id)
            if len(found) != len(set(tag_ids_to_set)):
                found_ids = {t.id for t in found}
                missing = sorted(set(tag_ids_to_set) - found_ids)
                raise HTTPException(
                    status_code=400,
                    detail=f"Tags not found or not owned by user: {missing}",
                )

        # Apply changes
        if update_data:
            await self.note_repo.update_note(note, update_data)
        if tag_ids_to_set is not None:
            await self.note_repo.set_note_tags(note, tag_ids_to_set)

        await self.note_repo.db.commit()
        await self.note_repo.db.refresh(note)                              # full
        await self.note_repo.db.refresh(note, attribute_names=["tags"])    # tags
        return note


def get_note_service(note_repo: NoteRepository = Depends(get_note_repository)) -> NoteService:
    return NoteService(note_repo)

