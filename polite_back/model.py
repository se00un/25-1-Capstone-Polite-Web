# backend/polite_back/model.py

from sqlalchemy import Column, Integer, String, Text, Float, Enum, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import text 
from .database import Base
import enum
from datetime import datetime
from typing import Optional

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
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    original = Column(Text)
    logit_original = Column(Float)
    polite = Column(Text)
    logit_polite = Column(Float)
    selected_version = Column(Enum(VersionEnum))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    reply_to = Column(Integer, ForeignKey("comments.id"), nullable=True)
    parent = relationship("Comment", remote_side=[id], backref="replies")

    is_modified = Column(Boolean, default=False)

    is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
