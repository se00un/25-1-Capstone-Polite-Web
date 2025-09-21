# polite_back/routes/bert.py

import asyncio, torch
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from polite_back.models.bert_model import predict as _predict
from polite_back.model import Post
from polite_back.database import get_db

router = APIRouter()

# 동시 추론 제한 
_infer_gate = asyncio.Semaphore(1)

class TextInput(BaseModel):
    text: str = Field(..., min_length=1)
    post_id: int = Field(..., gt=0)
    threshold: Optional[float] = Field(None, ge=0.0, le=1.0)

@router.post("/bert/predict")
async def predict_sentiment(input: TextInput, db: AsyncSession = Depends(get_db)):
    try:
        res = await db.execute(select(Post).where(Post.id == input.post_id))
        post = res.scalar_one_or_none()
        if not post:
            raise HTTPException(status_code=404, detail="post not found")

        th = input.threshold if input.threshold is not None else float(post.threshold)

        # 동시성 게이트로 메모리 피크 제어
        async with _infer_gate:
            # 내부에서 inference_mode 사용(bert_model.py)
            pred, prob = _predict(input.text, threshold=th)

        return {
            "text": input.text,
            "post_id": input.post_id,
            "policy_mode": post.policy_mode,
            "threshold_applied": th,
            "predicted_class": pred,
            "probability": round(prob, 4),
            "over_threshold": bool(pred == 1),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))