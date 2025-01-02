from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, foreign, remote
from datetime import datetime
from typing import Optional
from sqlalchemy.sql import text
from sqlalchemy.sql.schema import CheckConstraint, ForeignKeyConstraint
from schemas import AuthType

Base = declarative_base()

# Constants
ALL_TOPICS = -1  # Special value for chat threads to indicate "all topics" view


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    # Nullable for Google auth users
    password = Column(String(255), nullable=True)
    google_id = Column(String(255), unique=True, nullable=True)
    auth_type = Column(Enum(AuthType), nullable=False, default=AuthType.NATIVE)
    registration_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    topics = relationship("Topic", back_populates="user")


class Topic(Base):
    __tablename__ = "topics"

    topic_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    topic_name = Column(String(255))
    creation_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="topics")
