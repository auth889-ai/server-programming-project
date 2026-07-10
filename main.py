# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Import db setup
from models import create_db_and_tables

# Import routers
from api.users import router as users_router
from api.workouts import router as workouts_router
from api.follows import router as follows_router
from api.auth import router as auth_router
from api.feed import router as feed_router

# Import middleware
from core.middleware import add_all_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App is starting up...")
    # This is the code that runs on startup
    create_db_and_tables()
    print("Database tables created.")
    yield  # This yield separates startup code from shutdown code
    print("App is shutting down...")

# Create the FastAPI app with lifespan
app = FastAPI(
    title="Workout Social API",
    description="SWE 4538 group 14 - social workout tracker with auth, follows and a realtime feed",
    version="1.0.0",
    lifespan=lifespan,
)

# Add all middleware (CORS + ResponseTime)
add_all_middleware(app)

# Mount routers under /api/*
app.include_router(auth_router, prefix="/api/auth")
app.include_router(users_router, prefix="/api/users")
app.include_router(workouts_router, prefix="/api/workouts")
app.include_router(follows_router, prefix="/api/follows")
app.include_router(feed_router, prefix="/api/feed")