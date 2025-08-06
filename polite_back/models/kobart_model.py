# polite_back/models/kobart_model.py
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
import torch

MODEL_NAME = "heloolkjdasklfjlasdf/slang-kobart"  

def get_kobart_model():
    tokenizer = PreTrainedTokenizerFast.from_pretrained(MODEL_NAME)
    model = BartForConditionalGeneration.from_pretrained(MODEL_NAME)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    return tokenizer, model, device