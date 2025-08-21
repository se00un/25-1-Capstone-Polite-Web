# polite_back/routes/comment.py

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, func, literal
from sqlalchemy.orm import aliased
from pydantic import BaseModel
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
        "like_count": 0,
        "hate_count": 0,
        "liked_by_me": False,
        "hated_by_me": False,
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
    viewer_user_id: str | None = Query(None, description="조회 사용자 ID (있으면 liked_by_me/hated_by_me 포함)"),
    db: AsyncSession = Depends(get_db),
):

    q_sp = select(model.SubPost).where(
        model.SubPost.post_id == post_id,
        model.SubPost.ord == section,
    )
    sp = (await db.execute(q_sp)).scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=404, detail="Section not found")

    base_comments = (
        select(model.Comment)
        .where(
            model.Comment.sub_post_id == sp.id,
            model.Comment.is_deleted.is_(False),
        )
        .order_by(asc(model.Comment.created_at), asc(model.Comment.id))
    )

    likes_sq = (
        select(model.Reaction.comment_id, func.count(model.Reaction.id).label("like_count"))
        .where(model.Reaction.reaction_type == "like")
        .group_by(model.Reaction.comment_id)
        .subquery()
    )
    hates_sq = (
        select(model.Reaction.comment_id, func.count(model.Reaction.id).label("hate_count"))
        .where(model.Reaction.reaction_type == "hate")
        .group_by(model.Reaction.comment_id)
        .subquery()
    )

    if viewer_user_id:
        my_like_sq = (
            select(model.Reaction.comment_id, func.count(model.Reaction.id).label("liked_by_me"))
            .where(
                model.Reaction.reaction_type == "like",
                model.Reaction.user_id == viewer_user_id,
            )
            .group_by(model.Reaction.comment_id)
            .subquery()
        )
        my_hate_sq = (
            select(model.Reaction.comment_id, func.count(model.Reaction.id).label("hated_by_me"))
            .where(
                model.Reaction.reaction_type == "hate",
                model.Reaction.user_id == viewer_user_id,
            )
            .group_by(model.Reaction.comment_id)
            .subquery()
        )

        stmt = (
            select(
                model.Comment,
                func.coalesce(likes_sq.c.like_count, 0).label("like_count"),
                func.coalesce(hates_sq.c.hate_count, 0).label("hate_count"),
                func.coalesce(my_like_sq.c.liked_by_me, 0).label("liked_by_me"),
                func.coalesce(my_hate_sq.c.hated_by_me, 0).label("hated_by_me"),
            )
            .select_from(model.Comment)
            .outerjoin(likes_sq, likes_sq.c.comment_id == model.Comment.id)
            .outerjoin(hates_sq, hates_sq.c.comment_id == model.Comment.id)
            .outerjoin(my_like_sq, my_like_sq.c.comment_id == model.Comment.id)
            .outerjoin(my_hate_sq, my_hate_sq.c.comment_id == model.Comment.id)
            .where(
                model.Comment.sub_post_id == sp.id,
                model.Comment.is_deleted.is_(False),
            )
            .order_by(asc(model.Comment.created_at), asc(model.Comment.id))
        )
    else:
        stmt = (
            select(
                model.Comment,
                func.coalesce(likes_sq.c.like_count, 0).label("like_count"),
                func.coalesce(hates_sq.c.hate_count, 0).label("hate_count"),
                literal(0).label("liked_by_me"),
                literal(0).label("hated_by_me"),
            )
            .select_from(model.Comment)
            .outerjoin(likes_sq, likes_sq.c.comment_id == model.Comment.id)
            .outerjoin(hates_sq, hates_sq.c.comment_id == model.Comment.id)
            .where(
                model.Comment.sub_post_id == sp.id,
                model.Comment.is_deleted.is_(False),
            )
            .order_by(asc(model.Comment.created_at), asc(model.Comment.id))
        )

    rows = (await db.execute(stmt)).all()

    results = []
    for c, like_count, hate_count, liked_by_me, hated_by_me in rows:
        d = comment_to_dict(c, section=sp.ord)
        d["like_count"] = int(like_count or 0)
        d["hate_count"] = int(hate_count or 0)
        d["liked_by_me"] = bool(liked_by_me)
        d["hated_by_me"] = bool(hated_by_me)
        results.append(d)

    return results

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

class ToggleReq(BaseModel):
    user_id: str

async def _reaction_counts_and_flags(db: AsyncSession, comment_id: int, user_id: str):
    like_count_stmt = select(func.count(model.Reaction.id)).where(
        model.Reaction.comment_id == comment_id,
        model.Reaction.reaction_type == "like",
    )
    hate_count_stmt = select(func.count(model.Reaction.id)).where(
        model.Reaction.comment_id == comment_id,
        model.Reaction.reaction_type == "hate",
    )
    like_count = (await db.execute(like_count_stmt)).scalar_one() or 0
    hate_count = (await db.execute(hate_count_stmt)).scalar_one() or 0

    liked_stmt = select(func.count(model.Reaction.id)).where(
        model.Reaction.comment_id == comment_id,
        model.Reaction.user_id == user_id,
        model.Reaction.reaction_type == "like",
    )
    hated_stmt = select(func.count(model.Reaction.id)).where(
        model.Reaction.comment_id == comment_id,
        model.Reaction.user_id == user_id,
        model.Reaction.reaction_type == "hate",
    )
    liked_by_me = (await db.execute(liked_stmt)).scalar_one() or 0
    hated_by_me = (await db.execute(hated_stmt)).scalar_one() or 0

    return {
        "comment_id": comment_id,
        "like_count": int(like_count),
        "hate_count": int(hate_count),
        "liked_by_me": bool(liked_by_me),
        "hated_by_me": bool(hated_by_me),
    }

async def _ensure_comment_exists(db: AsyncSession, comment_id: int):
    stmt = select(model.Comment.id).where(model.Comment.id == comment_id)
    if (await db.execute(stmt)).scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Comment not found")

@router.post("/comments/{comment_id}/like")
async def toggle_like(comment_id: int, payload: ToggleReq, db: AsyncSession = Depends(get_db)):
    await _ensure_comment_exists(db, comment_id)

    find_stmt = select(model.Reaction).where(
        model.Reaction.comment_id == comment_id,
        model.Reaction.user_id == payload.user_id,
        model.Reaction.reaction_type == "like",
    )
    existing = (await db.execute(find_stmt)).scalar_one_or_none()

    if existing:
        db.delete(existing)
    else:
        db.add(model.Reaction(comment_id=comment_id, user_id=payload.user_id, reaction_type="like"))

    await db.commit()
    return await _reaction_counts_and_flags(db, comment_id, payload.user_id)

@router.post("/comments/{comment_id}/hate")
async def toggle_hate(comment_id: int, payload: ToggleReq, db: AsyncSession = Depends(get_db)):
    await _ensure_comment_exists(db, comment_id)

    find_stmt = select(model.Reaction).where(
        model.Reaction.comment_id == comment_id,
        model.Reaction.user_id == payload.user_id,
        model.Reaction.reaction_type == "hate",
    )
    existing = (await db.execute(find_stmt)).scalar_one_or_none()

    if existing:
        await db.delete(existing)
    else:
        db.add(model.Reaction(comment_id=comment_id, user_id=payload.user_id, reaction_type="hate"))

    await db.commit()
    return await _reaction_counts_and_flags(db, comment_id, payload.user_id)