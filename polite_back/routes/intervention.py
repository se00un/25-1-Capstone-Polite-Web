# polite_back/routes/intervention.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from polite_back.database import get_db
from polite_back.model import InterventionEvent, DecisionRule, FinalChoiceHint

router = APIRouter(prefix="/intervention-events", tags=["InterventionEvents"])

KST_TZ = timezone(timedelta(hours=9))

@router.post("")
async def log_intervention(payload: dict, db: AsyncSession = Depends(get_db)):
    """
    payload 예시:
    {
      "user_id": 123,
      "post_id": 7,
      "article_ord": 2,
      "temp_uuid": "client-uuid",
      "attempt_no": 1,
      "original_logit": 0.92,
      "threshold_applied": 0.5,
      "action_applied": "blocked"|"none",
      "generated_polite_text": "...",              # 순화 완료시
      "user_edit_text": "...", "edit_logit": 0.74, # 수정 시도시
      "decision_rule_applied": "forced_accept_one_edit"|"none",
      "final_choice_hint": "polite"|"user_edit"|"original"|"unknown",
      "latency_ms": 320
    }
    """
    ev = InterventionEvent(
      user_id=payload["user_id"],
      post_id=payload["post_id"],
      article_ord=payload["article_ord"],
      temp_uuid=payload.get("temp_uuid", "na"),
      attempt_no=payload.get("attempt_no", 1),
      original_logit=payload.get("original_logit"),
      threshold_applied=payload.get("threshold_applied"),
      action_applied=payload.get("action_applied", "none"),
      generated_polite_text=payload.get("generated_polite_text"),
      user_edit_text=payload.get("user_edit_text"),
      edit_logit=payload.get("edit_logit"),
      decision_rule_applied=DecisionRule(payload.get("decision_rule_applied", "none")),
      final_choice_hint=FinalChoiceHint(payload.get("final_choice_hint", "unknown")),
      latency_ms=payload.get("latency_ms"),
      shown_at=datetime.now(KST_TZ),
    )
    db.add(ev)
    await db.commit()
    return {"logged": True, "id": ev.id}
