# core/rate_limiter.py

import os
import redis
from fastapi import HTTPException

# Redis connection (defaults match docker-compose's exposed port on the host;
# set REDIS_HOST=redis and REDIS_PORT=6379 when running inside the compose network)
redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST", "127.0.0.1"),
    port=int(os.environ.get("REDIS_PORT", "6380")),
    decode_responses=True
)

def check_workout_rate_limit(user_id: int):

    """
    Limit workout creation
    Max 5 requests per 60 seconds
    """

    key = f"workout_limit:{user_id}"

    # increment counter
    count = redis_client.incr(key)

    # set TTL on first request
    if count == 1:
        redis_client.expire(key, 60)

    # block if limit exceeded
    if count > 5:
        raise HTTPException(
            status_code=429,
            detail="Too many workout posts. Try again later."
        )