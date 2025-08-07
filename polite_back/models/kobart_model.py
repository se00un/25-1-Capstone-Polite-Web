# polite_back/models/kobart_model.py

from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
import torch

MODEL_NAME = "heloolkjdasklfjlasdf/slang-kobart"

# 모델과 토크나이저를 처음 import 시점에 로딩
tokenizer = PreTrainedTokenizerFast.from_pretrained(MODEL_NAME)
model = BartForConditionalGeneration.from_pretrained(MODEL_NAME)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# 함수는 단순 반환만!
def get_kobart_model():
    return tokenizer, model, device