# polite_back/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text

from polite_back.routes.bert import router as bert_router
from polite_back.routes.kobart import router as kobart_router
from polite_back.routes.comment import router as comment_router
from polite_back.routes.users import router as user_router
from polite_back.routes.post import router as post_router
from polite_back.routes.intervention import router as intervention_router
from polite_back.routes.reaction import router as reaction_router
from polite_back.routes.reward import router as reward_router
from polite_back.database import engine

# 앱 라이프사이클: DB 연결 체크 / 종료 정리 
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"[startup] DB connection check failed: {e}")
    yield
    await engine.dispose()

app = FastAPI(title="Polite_Backend", lifespan=lifespan)

# CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://25-1-polite-web.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(bert_router)      
app.include_router(kobart_router)   
app.include_router(comment_router)  
app.include_router(user_router)     
app.include_router(post_router) 
app.include_router(intervention_router)     
app.include_router(reaction_router)
app.include_router(reward_router)

@app.get("/")
def read_root():
    return {"message": "Polite_Web 서버 실행 중"}
