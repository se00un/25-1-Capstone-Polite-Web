# polite-back/routes/comment.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from polite_back import model
from polite_back.database import get_db
from polite_back.schemas.schemas import CommentCreate, CommentOut
import requests
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

router = APIRouter()

@router.post("/comments/add", response_model=CommentOut)
def add_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    # 1. 프론트에서 넘겨준 감정/순화 결과값들을 그대로 저장
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
    # 2. DB 저장
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

@router.get("/comments/{post_id}", response_model=list[CommentOut])
def get_comments_by_post(post_id: int, db: Session = Depends(get_db)):
    return db.query(model.Comment).filter(model.Comment.post_id == post_id).all()

@router.get("/comments", response_model=list[CommentOut])
def get_all_comments(db: Session = Depends(get_db)):
    comments = db.query(model.Comment).all()
    return comments