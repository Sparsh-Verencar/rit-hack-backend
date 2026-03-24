from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.database import db

router = APIRouter()

class UserSyncPayload(BaseModel):
    userId: str # Sending ID directly from frontend
    email: str
    name: str | None = None
    imageUrl: str | None = None

@router.post("/users/sync")
async def sync_user(payload: UserSyncPayload):
    try:
        user = await db.user.upsert(
            where={"id": payload.userId},
            data={
                "create": {
                    "id": payload.userId,
                    "email": payload.email,
                    "name": payload.name,
                    "imageUrl": payload.imageUrl,
                },
                "update": {
                    "email": payload.email,
                    "name": payload.name,
                    "imageUrl": payload.imageUrl,
                }
            }
        )
        return {"status": "ok", "user": user.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))