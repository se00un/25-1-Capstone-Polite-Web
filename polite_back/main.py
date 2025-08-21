from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from polite_back.routes.bert import router as bert_router
from polite_back.routes.kobart import router as kobart_router
from polite_back.routes.comment import router as comment_router
from polite_back.routes.users import router as user_router
from polite_back.routes.post import router as post_router  
from polite_back import model
from polite_back.database import engine

import asyncio

app = FastAPI()

'''
# startup 시 비동기 테이블 생성
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(model.Base.metadata.create_all)
'''

# CORS 허용 (프론트 주소로 수정 가능)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://25-1-polite-web.netlify.app", ],
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

@app.get("/")
def read_root():
    return {"message": "Polite_Web 서버 실행 중"}


