from fastapi import FastAPI
from database import engine
import models

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Polite_Web 서버 실행 중"}

