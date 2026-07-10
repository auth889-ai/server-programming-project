# api/feed.py
from fastapi import (
    APIRouter,
    Depends,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from datetime import datetime, timezone
from typing import Dict
from jose import jwt, JWTError

from models import User, Workout, engine
from core.auth import get_current_user, SECRET_KEY, ALGORITHM
from core.realtime import notifier, event_generator, manager
from api.schemas import FeedCheckResponse

router = APIRouter(tags=["feed"])

def get_session():
    with Session(engine) as session:
        yield session

# In-memory storage for last checked timestamps per user
user_last_checked: Dict[int, datetime] = {}

@router.get("/check-new", response_model=FeedCheckResponse)
def check_new_workouts(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Check if new workouts exist since last check.
    Client can poll this endpoint every 10 seconds.
    """
    # Get all workouts excluding user's own
    workouts = session.exec(
        select(Workout).where(Workout.owner_id != current_user.id)
    ).all()
    
    total_workouts = len(workouts)
    
    # Simple logic: Check if there are any workouts
    has_new = True if total_workouts > 0 else False
    
    # Update the last checked time with timezone-aware datetime
    now = datetime.now(timezone.utc)
    user_last_checked[current_user.id] = now
    
    return FeedCheckResponse(
        has_new_workouts=has_new,
        last_checked=now.isoformat(),
        total_workouts=total_workouts
    )


# NEW: SSE ENDPOINT FOR TASK 2
@router.get("/stream/global-hype")
async def stream_global_hype(request: Request):
    """
    Server-Sent Events (SSE) endpoint for real-time workout notifications.
    Yields messages like "Athlete X just ran 10km!" whenever a workout is posted.
    
    Client connects with: new EventSource('/api/feed/stream/global-hype')
    """
    # Subscribe to notifications
    msg_queue = await notifier.subscribe()
    
    # Create event generator
    events = event_generator(request, msg_queue)
    
    # Return as Server-Sent Events stream
    return StreamingResponse(
        events,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Important for some proxies
        }
        
    )

@router.websocket("/ws/feed")
async def websocket_feed(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for personalized feed
    """

    # 1. Verify JWT
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return

    # 2. Get user from DB
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            await websocket.close(code=1008)
            return

        user_id = user.id

    # 3. Connect user
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "clap" and data.get("target_user_id"):
                target_id = data["target_user_id"]
                await manager.send_personal_message(
                    target_id,
                    {
                        "type": "clap",
                        "from_user_id": user_id,
                        "emoji": "👏"
                    }
                )

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)