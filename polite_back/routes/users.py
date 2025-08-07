# polite_back/routes/users.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from polite_back.database import get_db
from polite_back.model import User
from polite_back.schemas.schemas import UserCreate

router = APIRouter()

@router.post("/users/register")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user.user_id))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="User ID already exists")

    new_user = User(id=user.user_id)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User created", "user_id": new_user.id}

@router.post("/users/verify")
async def verify_user(data: dict, db: AsyncSession = Depends(get_db)):
    user_id = data["user_id"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return {"exists": user is not None}
