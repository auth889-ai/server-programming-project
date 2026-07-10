import os
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, create_engine
# Lab 4, Task 1
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime


# Database Setup (Moved here to avoid circular imports)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://swe_user:swe_pass@db:5432/swe_db")
engine = create_engine(DATABASE_URL, echo=True)


# -----------------------curl -i http://localhost:8000/api/users

# User Model
# -----------------------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    username: str = Field(index=True, unique=True)
    password_hash: Optional[str] = None  # Will be used in Lab 2

    # Relationships
    workouts: List["Workout"] = Relationship(back_populates="owner")
    following: List["Follow"] = Relationship(
        back_populates="follower", 
        sa_relationship_kwargs={"primaryjoin": "User.id==Follow.follower_id"}
    )
    followers: List["Follow"] = Relationship(
        back_populates="following",
        sa_relationship_kwargs={"primaryjoin": "User.id==Follow.following_id"}
    )


# -----------------------
# Workout Model
# -----------------------
class Workout(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    distance_km: float
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),  # FIXED
        sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  
    )

    owner_id: int = Field(foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="workouts")


# -----------------------
# Follow Model
# -----------------------
class Follow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    follower_id: int = Field(foreign_key="user.id")
    following_id: int = Field(foreign_key="user.id")

    follower: Optional[User] = Relationship(
        back_populates="following",
        sa_relationship_kwargs={"primaryjoin": "Follow.follower_id==User.id"}
    )
    following: Optional[User] = Relationship(
        back_populates="followers",
        sa_relationship_kwargs={"primaryjoin": "Follow.following_id==User.id"}
    )


def create_db_and_tables():
    SQLModel.metadata.create_all(engine) 