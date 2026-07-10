from typing import Optional
from pydantic import BaseModel


# ---------------------------
# AUTH
# ---------------------------
class UserCreate(BaseModel):
    email: str
    password: str


class UserPublic(BaseModel):
    id: Optional[int]
    email: str
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------------------
# WORKOUTS
# ---------------------------
class WorkoutCreate(BaseModel):
    title: str
    description: str
    distance_km: float


class WorkoutPublic(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    distance_km: float
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True


# ---------------------------
# FOLLOWS
# ---------------------------
class FollowPublic(BaseModel):
    id: Optional[int] = None
    follower_id: Optional[int] = None   # set automatically
    following_id: int

    class Config:
        from_attributes = True


# Lab 4

# ---------------------------
# FEED (for Task 1)
# ---------------------------
class FeedCheckResponse(BaseModel):
    has_new_workouts: bool
    last_checked: Optional[str] = None
    total_workouts: Optional[int] = None