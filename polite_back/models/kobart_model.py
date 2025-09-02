# polite_back/models/kobart_model.py

from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
import torch
from typing import Optional, Tuple
import os

os.environ["HF_HOME"] = "/opt/render/project/.hf_cache"
os.environ["TRANSFORMERS_CACHE"] = "/opt/render/project/.hf_cache"
MODEL_NAME = "heloolkjdasklfjlasdf/slang-kobart"

_tokenizer: Optional[PreTrainedTokenizerFast] = None
_model: Optional[BartForConditionalGeneration] = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_kobart_model() -> Tuple[PreTrainedTokenizerFast, BartForConditionalGeneration, torch.device]:
    global _tokenizer, _model
    if _model is None:
        torch.set_num_threads(1)  # 1 CPU 환경 안정화
        _tokenizer = PreTrainedTokenizerFast.from_pretrained(MODEL_NAME)
        m = BartForConditionalGeneration.from_pretrained(MODEL_NAME)
        m.to(_device)
        _model = m.eval()
    return _tokenizer, _model, _device
