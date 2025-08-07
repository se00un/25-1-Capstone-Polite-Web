# polite_back/routes/kobart.py

from fastapi import APIRouter
from polite_back.schemas.request import InputText
from polite_back.models.kobart_model import get_kobart_model
import torch

router = APIRouter(prefix="/kobart", tags=["KoBART"])
tokenizer, model, device = get_kobart_model()

def refine_text(text: str) -> str:
    input_ids = tokenizer("[순화] " + text, return_tensors="pt", truncation=True).input_ids.to(device)
    with torch.no_grad():
        output = model.generate(input_ids, max_length=128, num_beams=5)
    return tokenizer.decode(output[0], skip_special_tokens=True)

@router.post("/generate")
async def generate_polite_text(input: InputText):
    polite_text = refine_text(input.text)
    return {"polite_text": polite_text}

