# polite_back/routes/kobart.py

import asyncio, torch
from fastapi import APIRouter
from polite_back.schemas.request import InputText
from polite_back.models.kobart_model import get_kobart_model

router = APIRouter(prefix="/kobart", tags=["KoBART"])
_infer_gate = asyncio.Semaphore(2) # 필요시 2로 업데이트  

def refine_text(text: str) -> str:
    tokenizer, model, device = get_kobart_model()
    input_text = "[순화] " + text
    # 동적 패딩(배치=1) 유지: padding 지정 안 함 
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to(device)
    with torch.inference_mode():  
        output = model.generate(input_ids, max_length=128, num_beams=5)  # 기존 설정 그대로 유지 
    return tokenizer.decode(output[0], skip_special_tokens=True)

@router.post("/generate")
async def generate_polite_text(input: InputText):
    async with _infer_gate:
        polite_text = refine_text(input.text)
    return {"polite_text": polite_text}
