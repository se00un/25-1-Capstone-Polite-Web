# backend/polite_back/model.py
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    Boolean,
    Float,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint, CheckConstraint, func

from .database import Base


# Enums (Postgres enum 타입과 이름을 맞춤)
class PolicyMode(str, enum.Enum):
    block = "block"
    polite_one_edit = "polite_one_edit"
    nofilter = "nofilter"

class DecisionRule(str, enum.Enum):
    none = "none"
    forced_accept_one_edit = "forced_accept_one_edit"

class FinalChoiceHint(str, enum.Enum):
    unknown = "unknown"
    polite = "polite"
    user_edit = "user_edit"
    original = "original"

class FinalSource(str, enum.Enum):
    original = "original"
    polite = "polite"
    user_edit = "user_edit"
    blocked = "blocked"
    nofilter = "nofilter"

class ReactionType(str, enum.Enum):
    like = "like"
    hate = "hate"


# users
class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    comments = relationship("Comment", back_populates="user")


# posts (포스트 단위 policy/threshold)
class Post(Base):
    __tablename__ = "posts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)  
    password_hash = Column(String(200))  
    policy_mode = Column(PGEnum(PolicyMode, name="policy_mode", create_type=False), nullable=False)
    threshold = Column(Integer if False else Float, nullable=False)  
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    sub_posts = relationship(
        "SubPost",
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="SubPost.ord",
    )
    comments = relationship("Comment", back_populates="post")
    events = relationship("InterventionEvent", back_populates="post")


# sub_posts (기사 슬롯 1/2/3, 콘텐츠는 프론트 템플릿에서 주입)
class SubPost(Base):
    __tablename__ = "sub_posts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    ord = Column(SmallInteger, nullable=False)  # 1,2,3
    template_key = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    post = relationship("Post", back_populates="sub_posts")
    comments = relationship("Comment", back_populates="sub_post", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("post_id", "ord", name="uk_sub_posts_post_ord"),
        CheckConstraint("ord in (1,2,3)", name="chk_sub_posts_ord"),
    )


# intervention_events (검출/개입 로그; 제출 전 단계)
class InterventionEvent(Base):
    __tablename__ = "intervention_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    post_id = Column(BigInteger, ForeignKey("posts.id"), nullable=False)

    # 어떤 기사 슬롯인지 (DDL에선 ord 숫자만 저장)
    article_ord = Column(SmallInteger, nullable=False)  # 1/2/3
    temp_uuid = Column(String(64), nullable=False)
    attempt_no = Column(Integer, nullable=False, default=1)

    original_logit = Column(Float if True else Integer, nullable=False)  # 파이썬 float로 매핑
    threshold_applied = Column(Float if True else Integer, nullable=False)

    shown_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    latency_ms = Column(Integer)  

    # A 전용
    action_applied = Column(String(7), nullable=False, default="none")  # 'none' | 'blocked'

    # B 전용
    generated_polite_text = Column(Text)        # nullable
    user_edit_text = Column(Text)               # nullable
    edit_logit = Column(Float if True else Integer)  # nullable
    decision_rule_applied = Column(
        PGEnum(DecisionRule, name="decision_rule", create_type=False),
        nullable=False,
        default=DecisionRule.none,
    )
    final_choice_hint = Column(
        PGEnum(FinalChoiceHint, name="final_choice_hint", create_type=False),
        nullable=False,
        default=FinalChoiceHint.unknown,
    )

    user = relationship("User")
    post = relationship("Post", back_populates="events")

    __table_args__ = (
        CheckConstraint("article_ord in (1,2,3)", name="chk_ie_article_ord"),
        CheckConstraint("attempt_no > 0", name="chk_ie_attempt_no"),
    )

# comments (최종 저장)
class Comment(Base):
    __tablename__ = "comments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    sub_post_id = Column(BigInteger, ForeignKey("sub_posts.id", ondelete="CASCADE"), nullable=True)
    article_ord = Column(SmallInteger, nullable=True)  # 1/2/3

    parent_comment_id = Column(BigInteger, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)

    text_original = Column(Text)
    text_generated_polite = Column(Text)
    text_user_edit = Column(Text)
    text_final = Column(Text)  

    final_source = Column(PGEnum(FinalSource, name="final_source", create_type=False), nullable=False)
    was_edited = Column(Boolean, nullable=False, default=False)

    original_logit = Column(Float if True else Integer)
    edit_logit = Column(Float if True else Integer)
    final_logit = Column(Float if True else Integer)
    threshold_applied = Column(Float if True else Integer)

    attempts_count = Column(Integer, nullable=False, default=1)
    submit_success = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True))

    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    sub_post = relationship("SubPost", back_populates="comments")
    parent_comment = relationship("Comment", remote_side=[id], backref="children", uselist=False)

    reactions = relationship(
        "Reaction",
        back_populates="comment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

# reactions
class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    comment_id = Column(BigInteger, ForeignKey("comments.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(128), nullable=False, index=True)

    reaction_type = Column(
        PGEnum(ReactionType, name="reaction_type", create_type=False),
        nullable=False,
        index=True,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True))

    comment = relationship("Comment", back_populates="reactions")

    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", "reaction_type", name="uq_reactions_one_type_per_user"),
    )

# Claim Reward
class RewardClaim(Base):
    __tablename__ = "reward_claims"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    claimed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String(20), nullable=False, default="granted")

    user = relationship("User")
    post = relationship("Post")

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_reward_claims_user"),
    )