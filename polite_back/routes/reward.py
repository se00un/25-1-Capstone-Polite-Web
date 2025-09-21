# polite_back/routes/reward.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict
import os

from polite_back.database import get_db
from polite_back.model import Comment, RewardClaim, Post
from polite_back.schemas.reward import (
    RewardEligibilityRequest, RewardEligibilityResponse, RewardGrantResponse
)

router = APIRouter(prefix="/rewards", tags=["Rewards"])

REWARD_URL = os.getenv("REWARD_OPENCHAT_URL", "")
REWARD_PW  = os.getenv("REWARD_OPENCHAT_PW", "")


async def _counts_by_section(db: AsyncSession, user_id: int, post_id: int) -> Dict[int, int]:
    conditions = [
        Comment.user_id == user_id,
        Comment.post_id == post_id,
        Comment.submit_success.is_(True),
        Comment.is_deleted.is_(False),
    ]

    q = (
        select(
            Comment.article_ord.label("ord"),
            func.count(Comment.id).label("cnt")
        )
        .where(*conditions)
        .group_by(Comment.article_ord)
    )
    res = await db.execute(q)
    rows = res.all()

    counts = {1: 0, 2: 0, 3: 0}
    for ord_, cnt in rows:
        try:
            k = int(ord_)
        except (TypeError, ValueError):
            continue
        if k in (1, 2, 3):
            counts[k] = int(cnt or 0)
    return counts


def _is_eligible(counts: Dict[int, int]) -> tuple[bool, int]:
    total = sum(counts.values())
    ok = (counts.get(1, 0) >= 3 and counts.get(2, 0) >= 3 and counts.get(3, 0) >= 3 and total >= 9)
    return ok, total


@router.post("/eligibility", response_model=RewardEligibilityResponse)
async def check_eligibility(req: RewardEligibilityRequest, db: AsyncSession = Depends(get_db)):
    # Post 존재 확인
    res = await db.execute(select(Post.id).where(Post.id == req.post_id))
    if res.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Post not found")

    counts = await _counts_by_section(db, req.user_id, req.post_id)
    ok, total = _is_eligible(counts)

    # 이미 수령했는지(user_id UNIQUE 정책)
    res2 = await db.execute(
        select(RewardClaim.id).where(RewardClaim.user_id == req.user_id).limit(1)
    )
    already = res2.scalar_one_or_none() is not None

    return RewardEligibilityResponse(
        eligible=ok,
        already_claimed=already,
        per_section_counts=counts,
        total_count=total,
    )


@router.post("/claim", response_model=RewardGrantResponse)
async def claim_reward(req: RewardEligibilityRequest, db: AsyncSession = Depends(get_db)):
    # Post 존재 확인
    res = await db.execute(select(Post.id).where(Post.id == req.post_id))
    if res.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # 이미 수령: 링크/비번 재노출
    res_exist = await db.execute(
        select(RewardClaim).where(RewardClaim.user_id == req.user_id).limit(1)
    )
    existing = res_exist.scalar_one_or_none()
    if existing:
        return RewardGrantResponse(
            granted=False,
            already_claimed=True,
            openchat_url=REWARD_URL or None,
            openchat_pw=REWARD_PW or None,
        )

    # 자격 확인
    counts = await _counts_by_section(db, req.user_id, req.post_id)
    ok, _ = _is_eligible(counts)
    if not ok:
        return RewardGrantResponse(granted=False, already_claimed=False)

    # 수령 기록 저장 (user_id UNIQUE로 이중 보호)
    db.add(RewardClaim(user_id=req.user_id, post_id=req.post_id, status="granted"))
    await db.commit()

    return RewardGrantResponse(
        granted=True,
        already_claimed=False,
        openchat_url=REWARD_URL or None,
        openchat_pw=REWARD_PW or None,
    )