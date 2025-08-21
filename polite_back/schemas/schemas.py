# backend/schemas/schemas.py

from __future__ import annotations

from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime

class VersionEnum(str, Enum):
    original = "original"
    polite = "polite"

class UserCreate(BaseModel):
    user_id: str


class CommentBase(BaseModel):
    user_id: str
    post_id: int

    original: Optional[str] = None
    logit_original: Optional[float] = None

    polite: Optional[str] = None
    logit_polite: Optional[float] = None

    selected_version: Optional[VersionEnum] = None
    reply_to: Optional[int] = None
    is_modified: Optional[bool] = False


class CommentCreate(CommentBase):
    section: int 


class CommentOut(CommentBase):
    id: int
    created_at: datetime

    sub_post_id: Optional[int] = None
    section: Optional[int] = None  

    replies: List["CommentOut"] = []

    class Config:
        orm_mode = True


class SubPostOut(BaseModel):
    id: int
    ord: int
    title: Optional[str] = None
    content: Optional[str] = None
    created_at: datetime

    comments: Optional[List[CommentOut]] = None

    class Config:
        orm_mode = True


class PostDetail(BaseModel):
    id: int
    title: Optional[str] = None
    content: Optional[str] = None
    sections: List[SubPostOut]

    class Config:
        orm_mode = True


CommentOut.update_forward_refs()

