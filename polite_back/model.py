# backend/polite_back/model.py

from sqlalchemy import (
    Column, Integer, String, Text, Float, Enum as SAEnum,
    ForeignKey, DateTime, Boolean, SmallInteger, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy import text
from .database import Base
import enum
from datetime import datetime

class VersionEnum(str, enum.Enum):
    original = "original"
    polite = "polite"

class User(Base):
    __tablename__ = "users"

    id = Column(String(100), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    comments = relationship("Comment", back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    author_id = Column(String(100), nullable=True)
    password = Column(String(100))

    sub_posts = relationship(
        "SubPost",
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="SubPost.ord"
    )

    comments = relationship("Comment", back_populates="post")


class SubPost(Base):
    __tablename__ = "sub_posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    ord = Column(SmallInteger, nullable=False)  # 1,2,3
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    post = relationship("Post", back_populates="sub_posts")

    comments = relationship(
        "Comment",
        back_populates="sub_post",
        cascade="all, delete-orphan"
    )
    __table_args__ = (
        UniqueConstraint("post_id", "ord", name="uq_sub_posts_post_ord"),
    )

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))

    sub_post_id = Column(Integer, ForeignKey("sub_posts.id", ondelete="CASCADE"), nullable=False)

    original = Column(Text)
    logit_original = Column(Float)
    polite = Column(Text)
    logit_polite = Column(Float)
    selected_version = Column(SAEnum(VersionEnum), default=VersionEnum.original, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    reply_to = Column(Integer, ForeignKey("comments.id"), nullable=True)
    parent = relationship("Comment", remote_side=[id], backref="replies")

    is_modified = Column(Boolean, default=False)

    is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    sub_post = relationship("SubPost", back_populates="comments")
    reactions = relationship("Reaction", back_populates="comment", cascade="all, delete-orphan")

class Reaction(Base):
    __tablename__ = "comment_reactions"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(String(128), index=True, nullable=False)
    reaction_type = Column(SAEnum("like", "hate", name="reaction_type"), index=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", "reaction_type", name="uq_comment_user_reaction"),
    )

    comment = relationship("Comment", back_populates="reactions")