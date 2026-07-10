from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

from models import User, Follow, engine
from api.schemas import UserPublic, UserCreate
from core.auth import get_current_user, hash_password

router = APIRouter(tags=["users"])


def get_session():
    with Session(engine) as session:
        yield session


# Create user
@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)):

    existing_user = session.exec(
        select(User).where(User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    username = user.email.split("@")[0]

    new_user = User(
        email=user.email,
        username=username,
        password_hash=hash_password(user.password)
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return UserPublic(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username
    )


# List users
@router.get("/", response_model=List[UserPublic])
def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()

    return [
        UserPublic(id=u.id, email=u.email, username=u.username)
        for u in users
    ]


# Get single user
@router.get("/{user_id}", response_model=UserPublic)
def get_user(user_id: int, session: Session = Depends(get_session)):

    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserPublic(
        id=user.id,
        email=user.email,
        username=user.username
    )


# Delete user
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session)):

    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()

    return None


# ----------------------------
# Stretch Goal: Follow routes
# ----------------------------

@router.post("/{user_id}/follow")
def follow_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")

    target_user = session.get(User, user_id)

    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    existing_follow = session.exec(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_id
        )
    ).first()

    if existing_follow:
        raise HTTPException(status_code=400, detail="Already following this user")

    new_follow = Follow(
        follower_id=current_user.id,
        following_id=user_id
    )

    session.add(new_follow)
    session.commit()
    session.refresh(new_follow)

    return {"message": "Followed successfully"}


@router.delete("/{user_id}/follow")
def unfollow_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    follow = session.exec(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_id
        )
    ).first()

    if not follow:
        raise HTTPException(status_code=404, detail="Follow relationship not found")

    session.delete(follow)
    session.commit()

    return {"message": "Unfollowed successfully"}


@router.get("/{user_id}/followers", response_model=List[UserPublic])
def get_followers(user_id: int, session: Session = Depends(get_session)):

    followers = session.exec(
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
    ).all()

    return [
        UserPublic(id=u.id, email=u.email, username=u.username)
        for u in followers
    ]


@router.get("/{user_id}/following", response_model=List[UserPublic])
def get_following(user_id: int, session: Session = Depends(get_session)):

    following = session.exec(
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
    ).all()

    return [
        UserPublic(id=u.id, email=u.email, username=u.username)
        for u in following
    ]