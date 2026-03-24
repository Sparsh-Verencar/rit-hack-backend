import uuid
from fastapi import APIRouter, Depends, HTTPException
from core.security import get_current_user
from prisma import Prisma
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str
    r2_key: str  # The key where the frontend just uploaded the file


@router.post("")
async def create_project(data: ProjectCreate, user_id: str = Depends(get_current_user)):
    db = Prisma()
    await db.connect()

    try:
        # Create the project and the initial version (v0) in a transaction-like flow
        project = await db.project.create(
            data={
                "user_id": user_id,
                "name": data.name,
                "original_r2_key": data.r2_key,
                "row_count": 0,  # To be updated by a background worker if needed
                "col_count": 0,
                "columns": "{}",
            }
        )

        # Create Version 0 (The Raw Data)
        await db.projectversion.create(
            data={
                "project_id": project.id,
                "version_num": 0,
                "r2_key": data.r2_key,
                "status": "done",
                "row_count": 0,
                "col_count": 0,
                "summary": "Original file upload",
            }
        )

        return project
    finally:
        await db.disconnect()


@router.get("")
async def list_projects(user_id: str = Depends(get_current_user)):
    db = Prisma()
    await db.connect()
    try:
        projects = await db.project.find_many(
            where={"user_id": user_id}, order={"created_at": "desc"}
        )
        return projects
    finally:
        await db.disconnect()
