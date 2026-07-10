# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# # Import db setup
# from models import create_db_and_tables

# # Import routers explicitly
# from api.users import router as users_router
# from api.workouts import router as workouts_router
# from api.follows import router as follows_router
# from api.auth import router as auth_router

# app = FastAPI()


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # allow all origins (OK for lab/dev)
#     allow_credentials=True,
#     allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
#     allow_headers=["*"],  # Authorization, Content-Type, etc.
# )



# # Connect to main.py startup event
# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()


# # Mount routers under /api/*
# app.include_router(users_router, prefix="/api/users")
# app.include_router(workouts_router, prefix="/api/workouts")
# app.include_router(follows_router, prefix="/api/follows")
# app.include_router(auth_router, prefix="/api/auth")


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
app = FastAPI(lifespan=lifespan)

# Add all middleware (CORS + ResponseTime)
add_all_middleware(app)

# Mount routers under /api/*
app.include_router(auth_router, prefix="/api/auth")
app.include_router(users_router, prefix="/api/users")
app.include_router(workouts_router, prefix="/api/workouts")
app.include_router(follows_router, prefix="/api/follows")
app.include_router(feed_router, prefix="/api/feed")