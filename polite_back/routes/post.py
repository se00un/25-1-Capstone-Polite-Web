# polite_back/routes/post.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from polite_back.database import get_db
from polite_back.model import Post  

router = APIRouter()

@router.get("/posts")
async def get_all_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post))
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
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post or post.password != password:
        return {"valid": False}

    return {
        "valid": True,
        "post": {
            "id": post.id,
            "title": post.title,
            "content": post.content,
        }
    }
