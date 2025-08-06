# backend/routes/user.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from polite_back.database import get_db
from polite_back.model import User
from polite_back.schemas.schemas import UserCreate

router = APIRouter()

@router.post("/users/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.id == user.user_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User ID already exists")

    new_user = User(id=user.user_id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created", "user_id": new_user.id}

@router.post("/users/verify")
def verify_user(data: dict, db: Session = Depends(get_db)):
    user_id = data["user_id"]
    user = db.query(User).filter(User.id == user_id).first()
    return {"exists": user is not None}
