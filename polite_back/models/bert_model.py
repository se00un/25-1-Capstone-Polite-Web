# polite_back/models/bert_model.py

import torch
import torch.nn as nn
from transformers import ElectraTokenizer, ElectraModel
import json
import os

CACHE_DIR = os.environ.get("TRANSFORMERS_CACHE", "/tmp/huggingface/transformers")

# 욕설 사전 불러오기
base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, "word_list.json")
with open(json_path, "r", encoding="utf-8") as f:
    badword_dict = json.load(f)
badword_list = badword_dict["words"]

MODEL_NAME = "monologg/koelectra-base-v3-discriminator"
WEIGHTS_URL = "https://huggingface.co/H0jinPark/KoELECTRA-hatespeech/resolve/main/pytorch_model.bin"

# 전역 싱글톤 (지연 로딩)
_tokenizer = None
_model = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class KoElectraClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.electra = ElectraModel.from_pretrained(MODEL_NAME)
        self.classifier = nn.Linear(self.electra.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask):
        outputs = self.electra(input_ids=input_ids, attention_mask=attention_mask)
        cls_token = outputs.last_hidden_state[:, 0, :]
        logits = self.classifier(cls_token)
        return logits.squeeze(-1)

def _ensure_loaded():
    global _tokenizer, _model
    if _model is None:
        torch.set_num_threads(1)  
        _tokenizer = ElectraTokenizer.from_pretrained("H0jinPark/KoELECTRA-hatespeech")
        model = KoElectraClassifier()
        state_dict = torch.hub.load_state_dict_from_url(WEIGHTS_URL, map_location=_device)
        model.load_state_dict(state_dict)
        model.to(_device)
        _model = model.eval()

def predict(text, threshold=0.5):
    for word in badword_list:
        if word in text:
            return 1, 0.9

    _ensure_loaded()

    # 동적 패딩(배치=1에서는 PAD 불필요) + 길이는 기존과 동일하게 max_length=128 유지
    inputs = _tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    input_ids = inputs["input_ids"].to(_device)
    attention_mask = inputs["attention_mask"].to(_device)

    # inference_mode: 그래프/grad 버퍼 완전 OFF (출력 동일)
    with torch.inference_mode():
        logits = _model(input_ids=input_ids, attention_mask=attention_mask)
        prob = torch.sigmoid(logits)
        pred = (prob > threshold).int().item()

    # 임시 텐서 참조 해제(파편화 완화)
    del input_ids, attention_mask, logits

    return pred, float(prob.item())
