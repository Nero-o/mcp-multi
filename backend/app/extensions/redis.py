# app/extensions/redis.py
import os
import redis


def init_redis(app):
    redis_host = app.config.get("REDIS_HOST", "localhost")
    redis_port = app.config.get("REDIS_PORT", 6379)
    redis_username = app.config.get("REDIS_USERNAME", None)
    redis_password = app.config.get("REDIS_PASSWORD", None)

    redis_client = redis.Redis(
        host=redis_host,
        port=int(redis_port),
        username=redis_username,
        password=redis_password,
        db=0,
    )
    app.redis_client = redis_client
