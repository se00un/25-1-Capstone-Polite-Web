# polite_back/routes/comment.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from polite_back import model
from polite_back.database import get_db
from polite_back.schemas.schemas import CommentCreate
from datetime import datetime, timedelta

KST = timedelta(hours=9)

router = APIRouter()

@router.post("/comments/add")
async def add_comment(comment: CommentCreate, db: AsyncSession = Depends(get_db)):
    new_comment = model.Comment(
        user_id=comment.user_id,
        post_id=comment.post_id,
        original=comment.original,
        polite=comment.polite,
        logit_original=comment.logit_original,
        logit_polite=comment.logit_polite,
        selected_version=comment.selected_version,
        reply_to=comment.reply_to,
        is_modified=comment.is_modified,
        created_at=(datetime.utcnow() + KST).replace(tzinfo=None),
    )

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    # FastAPI가 response_model 쓰지 않고 dict로 보냄 → 오류 방지
    return {
        "message": "success",
        "comment": new_comment.__dict__
    }


@router.get("/comments/{post_id}")
async def get_comments_by_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(model.Comment).where(model.Comment.post_id == post_id)
    )
    flat_comments = result.scalars().all()

    return [c.__dict__ for c in flat_comments] 
