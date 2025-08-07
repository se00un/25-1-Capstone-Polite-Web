# polite_back/routes/comment.py
# 수정 확인용 주석

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from polite_back import model
from polite_back.database import get_db
from polite_back.schemas.schemas import CommentCreate, CommentOut
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

router = APIRouter()

@router.post("/comments/add", response_model=CommentOut)
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
        created_at=datetime.now(KST),
    )

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment

@router.get("/comments/{post_id}", response_model=list[CommentOut])
async def get_comments_by_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(model.Comment).where(model.Comment.post_id == post_id)
    )
    return result.scalars().all()

@router.get("/comments", response_model=list[CommentOut])
async def get_all_comments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(model.Comment))
    return result.scalars().all()
