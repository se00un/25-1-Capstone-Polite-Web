from pydantic import BaseModel, Field
from typing import List

class ToggleRequest(BaseModel):
    user_id: str = Field(..., min_length=1)

class ReactionStatusResponse(BaseModel):
    comment_id: int
    like_count: int
    hate_count: int
    liked_by_me: bool
    hated_by_me: bool

class BatchStatusRequest(BaseModel):
    user_id: str
    comment_ids: List[int]