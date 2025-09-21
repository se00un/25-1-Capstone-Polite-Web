# polite_back/routes/comment.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, and_, func, nulls_last, text
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone

from polite_back import model
from polite_back.database import get_db
from polite_back.models.bert_model import predict
from polite_back.routes.kobart import refine_text
from polite_back.schemas.schemas import SuggestReq, SuggestRes, SaveReq, SaveRes
from polite_back.model import FinalSource, Comment

router = APIRouter(prefix="/comments", tags=["Comments"])

KST_TZ = timezone(timedelta(hours=9))

def comment_to_dict(c: model.Comment,  section: Optional[int] = None) -> Dict[str, Any]:
    return {
        "id": c.id,
        "user_id": c.user_id,
        "post_id": c.post_id,
        "section": section if section is not None else getattr(c, "article_ord", None),
        "sub_post_id": getattr(c, "sub_post_id", None),
        "parent_comment_id": getattr(c, "parent_comment_id", None),

        "text_original": c.text_original,
        "text_generated_polite": c.text_generated_polite,
        "text_user_edit": c.text_user_edit,
        "text_final": c.text_final,

        "final_source": c.final_source.value if hasattr(c.final_source, "value") else c.final_source,
        "was_edited": bool(c.was_edited),

        "original_logit": c.original_logit,
        "edit_logit": c.edit_logit,
        "final_logit": c.final_logit,
        "threshold_applied": c.threshold_applied,

        "attempts_count": c.attempts_count,
        "submit_success": bool(c.submit_success),

        "created_at": c.created_at,
        "updated_at": c.updated_at,
    }


async def _require_subpost(db: AsyncSession, post_id: int, section: int) -> model.SubPost:
    stmt = select(model.SubPost).where(
        model.SubPost.post_id == post_id,
        model.SubPost.ord == section,
    )
    sp = (await db.execute(stmt)).scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=400, detail="Invalid post_id or section")
    return sp


async def _load_post(db: AsyncSession, post_id: int) -> model.Post:
    stmt = select(model.Post).where(model.Post.id == post_id)
    post = (await db.execute(stmt)).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="post not found")
    return post

async def _assert_user_locked_to_post(db: AsyncSession, user_id: int, post_id: int):
    row = await db.execute(
        select(model.Comment.post_id)
        .where(model.Comment.user_id == user_id)
        .limit(1)
    )
    first_post_id = row.scalar_one_or_none()
    if first_post_id is not None and int(first_post_id) != int(post_id):
        raise HTTPException(status_code=403, detail="User is locked to another post")


@router.post("/suggest", response_model=SuggestRes)
async def suggest(req: SuggestReq, db: AsyncSession = Depends(get_db)):
    post = await _load_post(db, req.post_id)
    th = float(post.threshold)

    # 공통: logit 계산
    over_pred, prob = predict(req.text, threshold=th)

    # A: block
    if post.policy_mode == "block":
        if over_pred:
            return SuggestRes(
                policy_mode="block",
                over_threshold=True,
                threshold_applied=th,
                message="차단되었습니다. 내용을 수정해 다시 시도하세요."
            )
        else:
            return SuggestRes(
                policy_mode="block",
                over_threshold=False,
                threshold_applied=th,
                message="통과 가능합니다."
            )

    # C: nofilter
    if post.policy_mode == "nofilter":
        return SuggestRes(
            policy_mode="nofilter",
            over_threshold=bool(over_pred),
            threshold_applied=th,
            message="무필터 모드입니다.",
            logit=prob
        )

    # B: polite_one_edit
    if over_pred:
        polite_text = refine_text(req.text)
        return SuggestRes(
            policy_mode="polite_one_edit",
            over_threshold=True,
            threshold_applied=th,
            polite_text=polite_text
        )
    else:
        return SuggestRes(
            policy_mode="polite_one_edit",
            over_threshold=False,
            threshold_applied=th,
            message="통과 가능합니다."
        )


@router.post("", response_model=SaveRes)
async def add_comment(req: SaveReq, db: AsyncSession = Depends(get_db)):
    post = await _load_post(db, req.post_id)
    th = float(post.threshold)
    sp = await _require_subpost(db, req.post_id, req.section)
    await _assert_user_locked_to_post(db, req.user_id, req.post_id)
    now_kst = datetime.now(KST_TZ)

    # A: block
    if post.policy_mode == "block":
        over_pred, prob = predict(req.text_original, threshold=th)
        if over_pred:
            new_comment = model.Comment(
                user_id=req.user_id,
                post_id=req.post_id,
                sub_post_id=sp.id,
                article_ord=req.section,
                parent_comment_id=getattr(req, "parent_comment_id", None),
                text_original=req.text_original,
                text_final=None,
                final_source=FinalSource.blocked,
                was_edited=False,
                original_logit=prob,
                final_logit=None,
                threshold_applied=th,
                attempts_count=1,
                submit_success=False,
                created_at=now_kst,
            )
            db.add(new_comment)
            await db.commit()
            await db.refresh(new_comment)
            return SaveRes(saved=False, final_source="blocked", comment_id=new_comment.id)

        # 통과 → original 저장
        new_comment = model.Comment(
            user_id=req.user_id,
            post_id=req.post_id,
            sub_post_id=sp.id,
            article_ord=req.section,
            parent_comment_id=getattr(req, "parent_comment_id", None),
            text_original=req.text_original,
            text_final=req.text_original,
            final_source=FinalSource.original,
            was_edited=False,
            original_logit=prob,
            final_logit=prob,
            threshold_applied=th,
            attempts_count=1,
            submit_success=True,
            created_at=now_kst,
        )
        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)
        return SaveRes(saved=True, final_source="original", comment_id=new_comment.id)

    # C: nofilter
    if post.policy_mode == "nofilter":
        over_pred, prob = predict(req.text_original, threshold=th)
        new_comment = model.Comment(
            user_id=req.user_id,
            post_id=req.post_id,
            sub_post_id=sp.id,
            article_ord=req.section,
            parent_comment_id=getattr(req, "parent_comment_id", None),
            text_original=req.text_original,
            text_final=req.text_original,
            final_source=FinalSource.nofilter, 
            was_edited=False,
            original_logit=prob,
            final_logit=prob,
            threshold_applied=th,
            attempts_count=1,
            submit_success=True,
            created_at=now_kst,
        )
        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)
        return SaveRes(saved=True, final_source="nofilter", comment_id=new_comment.id)


    # B: polite_one_edit
    over_pred, prob_orig = predict(req.text_original, threshold=th)
    if not over_pred:
        # 미만이면 개입 없이 original 저장
        new_comment = model.Comment(
            user_id=req.user_id,
            post_id=req.post_id,
            sub_post_id=sp.id,
            article_ord=req.section,
            parent_comment_id=getattr(req, "parent_comment_id", None),  
            text_original=req.text_original,
            text_final=req.text_original,
            final_source=FinalSource.original,
            was_edited=False,
            original_logit=prob_orig,
            final_logit=prob_orig,
            threshold_applied=th,
            attempts_count=1,
            submit_success=True,
            created_at=now_kst,
        )
        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)
        return SaveRes(saved=True, final_source="original", comment_id=new_comment.id)

    # 기준 초과 → 제안문 필요
    polite_text = req.generated_polite_text or refine_text(req.text_original)

    # 1회 수정이 있으면 평가
    if req.text_user_edit:
        over_edit, prob_edit = predict(req.text_user_edit, threshold=th)
        if not over_edit:
            # 수정본 채택
            new_comment = model.Comment(
                user_id=req.user_id,
                post_id=req.post_id,
                sub_post_id=sp.id,
                article_ord=req.section,
                parent_comment_id=getattr(req, "parent_comment_id", None),  
                text_original=req.text_original,
                text_generated_polite=polite_text,
                text_user_edit=req.text_user_edit,
                text_final=req.text_user_edit,
                final_source=FinalSource.user_edit,
                was_edited=True,
                original_logit=prob_orig,
                edit_logit=prob_edit,
                final_logit=prob_edit,
                threshold_applied=th,
                attempts_count=1,
                submit_success=True,
                created_at=now_kst,
            )
            db.add(new_comment)
            await db.commit()
            await db.refresh(new_comment)
            return SaveRes(saved=True, final_source="user_edit", comment_id=new_comment.id)

        # 수정안이 임계 초과 → 순화문으로 저장 (was_edited=False로 기록됨)
        prob_polite = predict(polite_text, threshold=th)[1]
        new_comment = model.Comment(
            user_id=req.user_id,
            post_id=req.post_id,
            sub_post_id=sp.id,
            article_ord=req.section,
            parent_comment_id=getattr(req, "parent_comment_id", None),  
            text_original=req.text_original,
            text_generated_polite=polite_text,
            text_user_edit=req.text_user_edit,
            text_final=polite_text,
            final_source=FinalSource.polite,
            was_edited=False,  # 강제 순화 채택이므로 '편집본 채택 아님'
            original_logit=prob_orig,
            edit_logit=prob_edit,
            final_logit=prob_polite,
            threshold_applied=th,
            attempts_count=1,
            submit_success=True,
            created_at=now_kst,
        )
        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)
        return SaveRes(saved=True, final_source="polite", comment_id=new_comment.id)

    # 수정 없음 → 제안문(순화문) 채택
    prob_polite = predict(polite_text, threshold=th)[1]
    new_comment = model.Comment(
        user_id=req.user_id,
        post_id=req.post_id,
        sub_post_id=sp.id,
        article_ord=req.section,
        parent_comment_id=getattr(req, "parent_comment_id", None),  
        text_original=req.text_original,
        text_generated_polite=polite_text,
        text_final=polite_text,
        final_source=FinalSource.polite,
        was_edited=False,
        original_logit=prob_orig,
        final_logit=prob_polite,
        threshold_applied=th,
        attempts_count=1,
        submit_success=True,
        created_at=now_kst,
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return SaveRes(saved=True, final_source="polite", comment_id=new_comment.id)


@router.get("", response_model=List[Dict[str, Any]])
async def get_comments_by_post(
    post_id: int = Query(..., gt=0),
    section: int = Query(..., ge=1, le=3, description="섹션(ord) 번호: 1|2|3"),
    include_deleted: bool = Query(False, description="소프트 삭제 포함 여부"),
    db: AsyncSession = Depends(get_db),
):
    sp = await _require_subpost(db, post_id, section)

    stmt = (
        select(model.Comment)
        .where(
            model.Comment.sub_post_id == sp.id,
            (model.Comment.is_deleted == False) if not include_deleted else text("TRUE"),
            (model.Comment.submit_success == True),
        )
        .order_by(asc(model.Comment.created_at), asc(model.Comment.id))
    )
    rows = (await db.execute(stmt)).scalars().all()

    return [comment_to_dict(c, section=section) for c in rows]

@router.delete("/{comment_id}")
async def soft_delete_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(model.Comment).where(model.Comment.id == comment_id)
    c = (await db.execute(stmt)).scalar_one_or_none()
    if not c:
        raise HTTPException(404, "Comment not found")

    if getattr(c, "is_deleted", False):
        return {"deleted": True, "already": True, "comment_id": comment_id}

    c.is_deleted = True
    c.deleted_at = datetime.now(KST_TZ)
    await db.commit()
    return {"deleted": True, "comment_id": comment_id}