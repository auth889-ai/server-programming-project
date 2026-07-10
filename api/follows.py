from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

from models import Follow, User, engine
from api.schemas import FollowPublic
from core.auth import get_current_user

router = APIRouter(tags=["follows"])


def get_session():
    with Session(engine) as session:
        yield session



@router.post("/", response_model=FollowPublic, status_code=201)
def create_follow(
    follow: FollowPublic,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    if follow.following_id == current_user.id:
        raise HTTPException(400, "You cannot follow yourself")

    new_follow = Follow(
        follower_id=current_user.id,
        following_id=follow.following_id
    )

    session.add(new_follow)
    session.commit()
    session.refresh(new_follow)

    return new_follow


@router.get("/", response_model=List[Follow])
def list_follows(session: Session = Depends(get_session)):
    return session.exec(select(Follow)).all()


@router.get("/{follow_id}", response_model=Follow)
def get_follow(follow_id: int, session: Session = Depends(get_session)):

    follow = session.get(Follow, follow_id)

    if not follow:
        raise HTTPException(status_code=404, detail="Follow not found")

    return follow


@router.delete("/{follow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_follow(follow_id: int, session: Session = Depends(get_session)):

    follow = session.get(Follow, follow_id)

    if not follow:
        raise HTTPException(status_code=404, detail="Follow not found")

    session.delete(follow)
    session.commit()

    return None