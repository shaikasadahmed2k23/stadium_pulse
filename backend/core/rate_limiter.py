"""
Shared rate limiter instance. Kept in its own module (not main.py) to
avoid circular imports between main.py and the API route files that
need to apply @limiter.limit(...) decorators.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
