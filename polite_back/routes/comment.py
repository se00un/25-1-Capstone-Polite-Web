# polite_back/routes/comment.py

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from polite_back import model
from polite_back.database import get_db
from polite_back.schemas.schemas import CommentCreate
from datetime import datetime, timedelta
from typing import Dict, Any, List

KST = timedelta(hours=9)
router = APIRouter()

def comment_to_dict(c: model.Comment, section: int | None = None) -> Dict[str, Any]:
    return {
        "id": c.id,
        "user_id": c.user_id,
        "post_id": c.post_id,
        "sub_post_id": c.sub_post_id,
        "section": section,  
        "original": c.original,
        "logit_original": c.logit_original,
        "polite": c.polite,
        "logit_polite": c.logit_polite,
        "selected_version": (c.selected_version.value if c.selected_version else None),
        "created_at": c.created_at,
        "reply_to": c.reply_to,
        "is_modified": c.is_modified,
        "is_deleted": c.is_deleted,
        "deleted_at": c.deleted_at,
    }


@router.post("/comments/add")
async def add_comment(comment: CommentCreate, db: AsyncSession = Depends(get_db)):
    q_sp = select(model.SubPost).where(
        model.SubPost.post_id == comment.post_id,
        model.SubPost.ord == comment.section,
    )
    sp = (await db.execute(q_sp)).scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=400, detail="Invalid post_id or section")

    new_comment = model.Comment(
        user_id=comment.user_id,
        post_id=comment.post_id,
        sub_post_id=sp.id,  
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

    return {
        "message": "success",
        "comment": comment_to_dict(new_comment, section=sp.ord),
    }


@router.get("/comments/{post_id}")
async def get_comments_by_post(
    post_id: int,
    section: int = Query(..., ge=1, le=3, description="섹션(ord) 번호: 1|2|3"),
    db: AsyncSession = Depends(get_db),
):
    q_sp = select(model.SubPost).where(
        model.SubPost.post_id == post_id,
        model.SubPost.ord == section,
    )
    sp = (await db.execute(q_sp)).scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=404, detail="Section not found")

    q_comments = (
        select(model.Comment)
        .where(
            model.Comment.sub_post_id == sp.id,
            model.Comment.is_deleted.is_(False),
        )
        .order_by(asc(model.Comment.created_at), asc(model.Comment.id))
    )
    comments: List[model.Comment] = (await db.execute(q_comments)).scalars().all()

    return [comment_to_dict(c, section=sp.ord) for c in comments]

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    payload: dict = Body(...),  
    db: AsyncSession = Depends(get_db),
):
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    q = select(model.Comment).where(model.Comment.id == comment_id)
    c = (await db.execute(q)).scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")

    if c.is_deleted:
        return {"message": "already deleted"}

    if c.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your comment")

    c.is_deleted = True
    c.deleted_at = (datetime.utcnow() + KST).replace(tzinfo=None)
    await db.commit()

    return {"message": "success", "deleted_id": comment_id}