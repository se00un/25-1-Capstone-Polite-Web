# polite_back/routes/post.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from polite_back.database import get_db
from polite_back import model  
from sqlalchemy import asc

router = APIRouter()

@router.get("/posts")
async def get_all_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(model.Post))
    posts = result.scalars().all()
    return {
        "posts": [
            {
                "id": post.id,
                "title": post.title,
                "content": post.content,
            }
            for post in posts
        ]
    }

@router.post("/posts/{post_id}/verify")
async def verify_post_password(post_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    password = data.get("password")

    result = await db.execute(select(model.Post).where(model.Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post or post.password != password:
        return {"valid": False}

    result_sp = await db.execute(
        select(model.SubPost).where(model.SubPost.post_id == post_id).order_by(asc(model.SubPost.ord))
    )
    sub_posts = result_sp.scalars().all()

    return {
        "valid": True,
        "post": {
            "id": post.id,
            "title": post.title,
            "content": post.content,
        },
        "sub_posts": [
            {
                "id": sp.id,
                "ord": sp.ord,
                "content": sp.content,
            }
            for sp in sub_posts
        ]
    }