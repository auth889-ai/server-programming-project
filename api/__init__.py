# # from fastapi import APIRouter

# # from .users import router as users_router
# # from .workouts import router as workouts_router
# # from .follows import router as follows_router

# # router = APIRouter()
# # router.include_router(users_router, prefix="/users")
# # router.include_router(workouts_router, prefix="/workouts")
# # router.include_router(follows_router, prefix="/follows")

# # __all__ = ["router"]


# from fastapi import APIRouter
# from .auth import router as auth_router
# from .users import router as users_router
# from .workouts import router as workouts_router
# from .follows import router as follows_router

# router = APIRouter()

# # Include routers WITHOUT duplicate prefixes
# router.include_router(auth_router)  # Routes already have /auth prefix
# router.include_router(users_router, prefix="/users")
# router.include_router(workouts_router, prefix="/workouts")
# router.include_router(follows_router, prefix="/follows")

# __all__ = ["router"]


# api/__init__.py
from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .workouts import router as workouts_router
from .follows import router as follows_router
from .feed import router as feed_router  # NEW

router = APIRouter()

# Include routers WITHOUT duplicate prefixes
router.include_router(auth_router)  # Routes already have /auth prefix
router.include_router(users_router, prefix="/users")
router.include_router(workouts_router, prefix="/workouts")
router.include_router(follows_router, prefix="/follows")
router.include_router(feed_router, prefix="/feed")  # NEW

__all__ = ["router"]