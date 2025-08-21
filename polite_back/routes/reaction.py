# polite_back/routes/reaction.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from polite_back.database import get_db
from polite_back import model 
from polite_back.schemas.reaction import ToggleRequest, ReactionStatusResponse, BatchStatusRequest

Reaction = model.Reaction
Comment = model.Comment

router = APIRouter(prefix="/comments", tags=["Reactions"])

def _counts(db: Session, comment_id: int):
    like_count = db.query(func.count(Reaction.id)).filter(
        Reaction.comment_id == comment_id, Reaction.reaction_type == "like"
    ).scalar()
    hate_count = db.query(func.count(Reaction.id)).filter(
        Reaction.comment_id == comment_id, Reaction.reaction_type == "hate"
    ).scalar()
    return like_count or 0, hate_count or 0

def _flags(db: Session, comment_id: int, user_id: str):
    liked = db.query(Reaction.id).filter(
        Reaction.comment_id == comment_id,
        Reaction.user_id == user_id,
        Reaction.reaction_type == "like",
    ).first() is not None
    hated = db.query(Reaction.id).filter(
        Reaction.comment_id == comment_id,
        Reaction.user_id == user_id,
        Reaction.reaction_type == "hate",
    ).first() is not None
    return liked, hated

@router.post("/{comment_id}/like", response_model=ReactionStatusResponse)
def toggle_like(comment_id: int, req: ToggleRequest, db: Session = Depends(get_db)):
    if not db.query(Comment.id).filter(Comment.id == comment_id).first():
        raise HTTPException(status_code=404, detail="Comment not found")

    existing = db.query(Reaction).filter(
        Reaction.comment_id == comment_id,
        Reaction.user_id == req.user_id,
        Reaction.reaction_type == "like",
    ).first()

    if existing:
        db.delete(existing)
    else:
        db.add(Reaction(comment_id=comment_id, user_id=req.user_id, reaction_type="like"))
    db.commit()

    like_count, hate_count = _counts(db, comment_id)
    liked_by_me, hated_by_me = _flags(db, comment_id, req.user_id)

    return ReactionStatusResponse(
        comment_id=comment_id,
        like_count=like_count,
        hate_count=hate_count,
        liked_by_me=liked_by_me,
        hated_by_me=hated_by_me,
    )

@router.post("/{comment_id}/hate", response_model=ReactionStatusResponse)
def toggle_hate(comment_id: int, req: ToggleRequest, db: Session = Depends(get_db)):
    if not db.query(Comment.id).filter(Comment.id == comment_id).first():
        raise HTTPException(status_code=404, detail="Comment not found")

    existing = db.query(Reaction).filter(
        Reaction.comment_id == comment_id,
        Reaction.user_id == req.user_id,
        Reaction.reaction_type == "hate",
    ).first()

    if existing:
        db.delete(existing)
    else:
        db.add(Reaction(comment_id=comment_id, user_id=req.user_id, reaction_type="hate"))
    db.commit()

    like_count, hate_count = _counts(db, comment_id)
    liked_by_me, hated_by_me = _flags(db, comment_id, req.user_id)

    return ReactionStatusResponse(
        comment_id=comment_id,
        like_count=like_count,
        hate_count=hate_count,
        liked_by_me=liked_by_me,
        hated_by_me=hated_by_me,
    )

@router.get("/{comment_id}/reactions", response_model=ReactionStatusResponse)
def get_reaction_status(comment_id: int, user_id: str, db: Session = Depends(get_db)):
    if not db.query(Comment.id).filter(Comment.id == comment_id).first():
        raise HTTPException(status_code=404, detail="Comment not found")

    like_count, hate_count = _counts(db, comment_id)
    liked_by_me, hated_by_me = _flags(db, comment_id, user_id)

    return ReactionStatusResponse(
        comment_id=comment_id,
        like_count=like_count,
        hate_count=hate_count,
        liked_by_me=liked_by_me,
        hated_by_me=hated_by_me,
    )

@router.post("/reactions/batch", response_model=list[ReactionStatusResponse])
def get_batch_reaction_status(req: BatchStatusRequest, db: Session = Depends(get_db)):
    results = []
    for cid in req.comment_ids:
        if not db.query(Comment.id).filter(Comment.id == cid).first():
            continue
        like_count, hate_count = _counts(db, cid)
        liked_by_me, hated_by_me = _flags(db, cid, req.user_id)
        results.append(ReactionStatusResponse(
            comment_id=cid,
            like_count=like_count,
            hate_count=hate_count,
            liked_by_me=liked_by_me,
            hated_by_me=hated_by_me,
        ))
    return results
