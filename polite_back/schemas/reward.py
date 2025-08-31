# polite_back/schemas/reward.py

from pydantic import BaseModel, Field
from typing import Dict

class RewardEligibilityRequest(BaseModel):
    user_id: int
    post_id: int

class RewardEligibilityResponse(BaseModel):
    eligible: bool
    already_claimed: bool
    per_section_counts: Dict[int, int]   
    total_count: int

class RewardGrantResponse(BaseModel):
    granted: bool
    already_claimed: bool
    openchat_url: str | None = None
    openchat_pw: str | None = None
