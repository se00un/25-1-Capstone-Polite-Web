# polite_back/database.py

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,            
    connect_args={"ssl": True},
    pool_size=5,           # 기본 5: 필요시 3~5로 줄이기
    max_overflow=0, 
    pool_timeout=30,       
    pool_pre_ping=True,    
    pool_recycle=1800      
)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session

