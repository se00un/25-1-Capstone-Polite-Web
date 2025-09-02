# polite_back/routes/reaction.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone
from typing import List

from polite_back.database import get_db
from polite_back.model import Comment, Reaction, ReactionType
from polite_back.schemas.reaction import (
    ToggleRequest,
    ReactionStatusResponse,
    BatchStatusRequest,
)

router = APIRouter(prefix="/comments", tags=["Reactions"])


async def _ensure_comment_exists(db: AsyncSession, comment_id: int):
    res = await db.execute(select(Comment.id).where(Comment.id == comment_id))
    exists = res.scalar_one_or_none()
    if exists is None:
        raise HTTPException(status_code=404, detail="Comment not found")


async def _counts(db: AsyncSession, comment_id: int):
    # like count
    res_like = await db.execute(
        select(func.count(Reaction.id)).where(
            Reaction.comment_id == comment_id,
            Reaction.reaction_type == ReactionType.like,
        )
    )
    like_count = res_like.scalar_one() or 0

    # hate count
    res_hate = await db.execute(
        select(func.count(Reaction.id)).where(
            Reaction.comment_id == comment_id,
            Reaction.reaction_type == ReactionType.hate,
        )
    )
    hate_count = res_hate.scalar_one() or 0

    return like_count, hate_count


async def _flags(db: AsyncSession, comment_id: int, user_id: str):
    # liked?
    res_liked = await db.execute(
        select(Reaction.id)
        .where(
            Reaction.comment_id == comment_id,
            Reaction.user_id == user_id,
            Reaction.reaction_type == ReactionType.like,
        )
        .limit(1)
    )
    liked = res_liked.scalar_one_or_none() is not None

    # hated?
    res_hated = await db.execute(
        select(Reaction.id)
        .where(
            Reaction.comment_id == comment_id,
            Reaction.user_id == user_id,
            Reaction.reaction_type == ReactionType.hate,
        )
        .limit(1)
    )
    hated = res_hated.scalar_one_or_none() is not None

    return liked, hated


async def _toggle_same_type(db: AsyncSession, comment_id: int, user_id: str, rtype: ReactionType):
    res = await db.execute(
        select(Reaction)
        .where(
            Reaction.comment_id == comment_id,
            Reaction.user_id == user_id,
            Reaction.reaction_type == rtype,
        )
        .limit(1)
    )
    existing = res.scalar_one_or_none()

    if existing:
        await db.delete(existing)  
    else:
        now_ts = datetime.now(timezone.utc)
        db.add(
            Reaction(
                comment_id=comment_id,
                user_id=user_id,
                reaction_type=rtype,
                updated_at=now_ts,  
            )
        )
    await db.commit()


@router.post("/{comment_id}/like", response_model=ReactionStatusResponse)
async def toggle_like(
    comment_id: int, req: ToggleRequest, db: AsyncSession = Depends(get_db)
):
    await _ensure_comment_exists(db, comment_id)
    await _toggle_same_type(db, comment_id, req.user_id, ReactionType.like)
    like_count, hate_count = await _counts(db, comment_id)
    liked_by_me, hated_by_me = await _flags(db, comment_id, req.user_id)
    return ReactionStatusResponse(
        comment_id=comment_id,
        like_count=like_count,
        hate_count=hate_count,
        liked_by_me=liked_by_me,
        hated_by_me=hated_by_me,
    )


@router.post("/{comment_id}/hate", response_model=ReactionStatusResponse)
async def toggle_hate(
    comment_id: int, req: ToggleRequest, db: AsyncSession = Depends(get_db)
):
    await _ensure_comment_exists(db, comment_id)
    await _toggle_same_type(db, comment_id, req.user_id, ReactionType.hate)
    like_count, hate_count = await _counts(db, comment_id)
    liked_by_me, hated_by_me = await _flags(db, comment_id, req.user_id)
    return ReactionStatusResponse(
        comment_id=comment_id,
        like_count=like_count,
        hate_count=hate_count,
        liked_by_me=liked_by_me,
        hated_by_me=hated_by_me,
    )


@router.get("/{comment_id}/reactions", response_model=ReactionStatusResponse)
async def get_reaction_status(
    comment_id: int, user_id: str, db: AsyncSession = Depends(get_db)
):
    await _ensure_comment_exists(db, comment_id)
    like_count, hate_count = await _counts(db, comment_id)
    liked_by_me, hated_by_me = await _flags(db, comment_id, user_id)
    return ReactionStatusResponse(
        comment_id=comment_id,
        like_count=like_count,
        hate_count=hate_count,
        liked_by_me=liked_by_me,
        hated_by_me=hated_by_me,
    )


@router.post("/reactions/batch", response_model=List[ReactionStatusResponse])
async def get_batch_reaction_status(
    req: BatchStatusRequest, db: AsyncSession = Depends(get_db)
):
    results: List[ReactionStatusResponse] = []

    for cid in req.comment_ids:
        # 존재 확인
        res = await db.execute(select(Comment.id).where(Comment.id == cid))
        if res.scalar_one_or_none() is None:
            continue

        like_count, hate_count = await _counts(db, cid)
        liked_by_me, hated_by_me = await _flags(db, cid, req.user_id)

        results.append(
            ReactionStatusResponse(
                comment_id=cid,
                like_count=like_count,
                hate_count=hate_count,
                liked_by_me=liked_by_me,
                hated_by_me=hated_by_me,
            )
        )

    return results