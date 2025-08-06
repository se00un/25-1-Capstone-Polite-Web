# polite_back/models/bert_model.py

import torch
import torch.nn as nn
from transformers import ElectraTokenizer, ElectraModel
import json
import os

# 욕설 사전 불러오기
base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, "word_list.json")
with open(json_path, "r", encoding="utf-8") as f:
    badword_dict = json.load(f)
badword_list = badword_dict["words"]

MODEL_NAME = "monologg/koelectra-base-v3-discriminator"  

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

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = KoElectraClassifier()

# 허브에 올린 가중치 URL
WEIGHTS_URL = "https://huggingface.co/H0jinPark/KoELECTRA-hatespeech/resolve/main/pytorch_model.bin"

# 허브에서 가중치 다운로드 및 로드
state_dict = torch.hub.load_state_dict_from_url(WEIGHTS_URL, map_location=device)
model.load_state_dict(state_dict)

model.to(device)
model.eval()

tokenizer = ElectraTokenizer.from_pretrained("H0jinPark/KoELECTRA-hatespeech")

def predict(text, threshold=0.5):
    for word in badword_list:
        if word in text:
            return 1, 0.9

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=128)
    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)

    with torch.no_grad():
        logits = model(input_ids=input_ids, attention_mask=attention_mask)
        prob = torch.sigmoid(logits)
        pred = (prob > threshold).int().item()

    return pred, prob.item()