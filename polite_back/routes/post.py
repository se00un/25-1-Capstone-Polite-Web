# routes/post.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from polite_back.database import get_db
from polite_back.model import Post  

router = APIRouter()

@router.get("/posts")
def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
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
def verify_post_password(post_id: int, data: dict, db: Session = Depends(get_db)):
    password = data.get("password")
    post = db.query(Post).filter(Post.id == post_id).first()

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