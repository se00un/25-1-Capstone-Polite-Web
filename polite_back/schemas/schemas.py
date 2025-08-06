# backend/schemas.py

from pydantic import BaseModel
from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from datetime import datetime

if TYPE_CHECKING:
    from .schemas import CommentOut

class UserCreate(BaseModel):
    user_id: str

class VersionEnum(str, Enum):
    original = "original"
    polite = "polite"

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
    pass

class CommentOut(CommentBase):
    id: int
    created_at: datetime
    replies: List["CommentOut"] = [] 

    class Config:
        orm_mode = True


