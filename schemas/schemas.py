# backend/schemas/schemas.py

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class PolicyMode(str, Enum):
    block = "block"
    polite_one_edit = "polite_one_edit"
    nofilter = "nofilter"


class FinalSource(str, Enum):
    original = "original"
    polite = "polite"
    user_edit = "user_edit"
    blocked = "blocked"
    nofilter = "nofilter" 


class UserRegister(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)


class UserVerify(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    id: Optional[int] = None


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        orm_mode = True

class SuggestReq(BaseModel):
    post_id: int = Field(..., gt=0)
    section: int = Field(..., ge=1, le=3)  
    text: str = Field(..., min_length=1)


class SuggestRes(BaseModel):
    policy_mode: PolicyMode
    over_threshold: bool
    threshold_applied: float
    polite_text: Optional[str] = None
    message: Optional[str] = None
    logit: Optional[float] = None


class SaveReq(BaseModel):
    user_id: int = Field(..., gt=0)        
    post_id: int = Field(..., gt=0)
    section: int = Field(..., ge=1, le=3)  
    text_original: str = Field(..., min_length=1)
    parent_comment_id: Optional[int] = None

    # B 전용(무조건 수락 + 1회 수정)
    generated_polite_text: Optional[str] = None
    text_user_edit: Optional[str] = None


class SaveRes(BaseModel):
    saved: bool
    final_source: FinalSource
    comment_id: Optional[int] = None


class CommentOut(BaseModel):
    id: int
    user_id: int
    post_id: int

    sub_post_id: Optional[int] = None
    section: Optional[int] = None  

    text_original: Optional[str] = None
    text_generated_polite: Optional[str] = None
    text_user_edit: Optional[str] = None
    text_final: Optional[str] = None

    final_source: FinalSource
    was_edited: bool

    original_logit: Optional[float] = None
    edit_logit: Optional[float] = None
    final_logit: Optional[float] = None
    threshold_applied: Optional[float] = None

    attempts_count: int
    submit_success: bool

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True



class SubPostOut(BaseModel):
    id: int
    ord: int
    template_key: str
    created_at: datetime

    class Config:
        orm_mode = True


class PostDetail(BaseModel):
    id: int
    title: Optional[str] = None
    content: Optional[str] = None
    policy_mode: PolicyMode
    threshold: float
    sections: List[SubPostOut]

    class Config:
        orm_mode = True