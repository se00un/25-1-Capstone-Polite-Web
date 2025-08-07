# polite_back/routes/bert.py
# 수정 확인용 주석

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from polite_back.models.bert_model import predict

router = APIRouter()

class TextInput(BaseModel):
    text: str

@router.post("/bert/predict")
async def predict_sentiment(input: TextInput):
    try:
        pred, prob = predict(input.text, threshold=0.5)
        return {
            "text": input.text,
            "predicted_class": pred,
            "probability": round(prob, 4)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




