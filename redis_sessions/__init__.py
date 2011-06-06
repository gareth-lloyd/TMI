from redis import Redis
from django.conf import settings

redis_client = Redis(
    host=getattr(settings, "REDIS_SESSIONS_HOST", 'localhost'),
    port=getattr(settings, "REDIS_SESSIONS_PORT", 6379),
    socket_timeout=getattr(settings, "REDIS_SESSIONS_TIMEOUT", 10000),
    db=getattr(settings, "REDIS_SESSIONS_DB", 0),
    password=getattr(settings, "REDIS_PASSWORD", "")
)
