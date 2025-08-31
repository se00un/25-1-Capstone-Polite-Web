# polite_back/routes/reward.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

from polite_back.database import get_db
from polite_back.model import Comment, RewardClaim, Post
from polite_back.schemas.reward import (
    RewardEligibilityRequest, RewardEligibilityResponse, RewardGrantResponse
)

router = APIRouter(prefix="/rewards", tags=["Rewards"])

REWARD_URL = os.getenv("REWARD_OPENCHAT_URL", "")
REWARD_PW  = os.getenv("REWARD_OPENCHAT_PW", "")

def _counts_by_section(db: Session, user_id: int, post_id: int) -> dict[int, int]:
    rows = (
        db.query(
            Comment.article_ord.label("ord"),
            func.count(Comment.id).label("cnt")
        )
        .filter(
            Comment.user_id == user_id,
            Comment.post_id == post_id,
            Comment.submit_success.is_(True)
        )
        .group_by(Comment.article_ord)
        .all()
    )
    counts = {1: 0, 2: 0, 3: 0}
    for r in rows:
        if r.ord in (1, 2, 3):
            counts[int(r.ord)] = int(r.cnt)
    return counts

def _is_eligible(counts: dict[int, int]) -> tuple[bool, int]:
    total = sum(counts.values())
    ok = (counts.get(1, 0) >= 3 and counts.get(2, 0) >= 3 and counts.get(3, 0) >= 3 and total >= 9)
    return ok, total

@router.post("/eligibility", response_model=RewardEligibilityResponse)
def check_eligibility(req: RewardEligibilityRequest, db: Session = Depends(get_db)):
    if not db.query(Post.id).filter(Post.id == req.post_id).first():
        raise HTTPException(status_code=404, detail="Post not found")

    counts = _counts_by_section(db, req.user_id, req.post_id)
    ok, total = _is_eligible(counts)
    already = db.query(RewardClaim.id).filter(
        RewardClaim.user_id == req.user_id
    ).first() is not None  # user_id UNIQUE 정책

    return RewardEligibilityResponse(
        eligible=ok,
        already_claimed=already,
        per_section_counts=counts,
        total_count=total,
    )

@router.post("/claim", response_model=RewardGrantResponse)
def claim_reward(req: RewardEligibilityRequest, db: Session = Depends(get_db)):
    if not db.query(Post.id).filter(Post.id == req.post_id).first():
        raise HTTPException(status_code=404, detail="Post not found")

    # 이미 수령한 경우: 링크/비번 재노출(운영 편의)
    existing = db.query(RewardClaim).filter(RewardClaim.user_id == req.user_id).first()
    if existing:
        return RewardGrantResponse(
            granted=False,
            already_claimed=True,
            openchat_url=REWARD_URL or None,
            openchat_pw=REWARD_PW or None,
        )

    # 자격 확인
    counts = _counts_by_section(db, req.user_id, req.post_id)
    ok, _ = _is_eligible(counts)
    if not ok:
        return RewardGrantResponse(granted=False, already_claimed=False)

    # 수령 기록 저장 (user_id UNIQUE가 DB에서 2중 보호)
    db.add(RewardClaim(user_id=req.user_id, post_id=req.post_id, status="granted"))
    db.commit()

    return RewardGrantResponse(
        granted=True,
        already_claimed=False,
        openchat_url=REWARD_URL or None,
        openchat_pw=REWARD_PW or None,
    )
