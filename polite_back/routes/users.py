# polite_back/routes/users.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone
from typing import Optional
from polite_back.schemas.schemas import UserRegister, UserVerify

from polite_back.database import get_db
from polite_back.model import User

router = APIRouter(prefix="/users", tags=["Users"])
KST_TZ = timezone(timedelta(hours=9))

from pydantic import BaseModel, Field



@router.post("/register")
async def register_user(body: UserRegister, db: AsyncSession = Depends(get_db)):
    q = select(User).where(User.username == body.username)
    existing = (await db.execute(q)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(username=body.username, created_at=datetime.now(KST_TZ))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "message": "User created",
        "id": new_user.id,              
        "username": new_user.username,
        "created_at": new_user.created_at,
    }


@router.post("/verify")
async def verify_user(body: UserVerify, db: AsyncSession = Depends(get_db)):
    if body.username:
        q = select(User).where(User.username == body.username)
    elif body.id is not None:
        q = select(User).where(User.id == body.id)
    else:
        raise HTTPException(status_code=400, detail="Provide username or id")

    user = (await db.execute(q)).scalar_one_or_none()

    return {
        "exists": user is not None,
        "id": user.id if user else None,
        "username": user.username if user else None,
        "created_at": user.created_at if user else None,
    }