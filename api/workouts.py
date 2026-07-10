from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

from models import Workout, Follow, User, engine
from core.auth import get_current_user
from api.schemas import WorkoutCreate, WorkoutPublic
from core.realtime import manager

router = APIRouter(tags=["workouts"])


def get_session():
    with Session(engine) as session:
        yield session


async def broadcast_workout(workout: Workout, session: Session):

    followers = session.exec(
        select(Follow).where(
            Follow.following_id == workout.owner_id
        )
    ).all()

    payload = {
        "type": "workout",
        "athlete_id": workout.owner_id,
        "title": workout.title,
        "distance_km": workout.distance_km
    }

    for f in followers:
        await manager.send_to_user(
            user_id=f.follower_id,
            data=payload
        )


# Create workout
@router.post("/", response_model=WorkoutPublic, status_code=201)
async def create_workout(
    workout: WorkoutCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    new_workout = Workout(
        title=workout.title,
        description=workout.description,
        distance_km=workout.distance_km,
        owner_id=current_user.id
    )

    session.add(new_workout)
    session.commit()
    session.refresh(new_workout)

    await broadcast_workout(new_workout, session)

    return new_workout


# List workouts
@router.get("/", response_model=List[WorkoutPublic])
def list_workouts(session: Session = Depends(get_session)):
    return session.exec(select(Workout)).all()


# Get single workout
@router.get("/{workout_id}", response_model=WorkoutPublic)
def get_workout(workout_id: int, session: Session = Depends(get_session)):

    workout = session.get(Workout, workout_id)

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    return workout


# Update workout
@router.put("/{workout_id}", response_model=WorkoutPublic)
def update_workout(
    workout_id: int,
    workout_data: WorkoutCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    workout = session.get(Workout, workout_id)

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    if workout.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    workout.title = workout_data.title
    workout.description = workout_data.description
    workout.distance_km = workout_data.distance_km

    session.add(workout)
    session.commit()
    session.refresh(workout)

    return workout


# Delete workout
@router.delete("/{workout_id}")
def delete_workout(
    workout_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    workout = session.get(Workout, workout_id)

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    if workout.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    session.delete(workout)
    session.commit()

    return {"message": "Workout deleted"}