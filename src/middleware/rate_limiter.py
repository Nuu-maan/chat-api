from fastapi import HTTPException, Request
from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, Tuple[datetime, int]] = {}

    async def __call__(self, request: Request):
        """Rate limit based on client IP"""
        client_ip = request.client.host
        now = datetime.utcnow()

        # Get or initialize request count for this IP
        if client_ip in self.requests:
            last_request_time, count = self.requests[client_ip]
            # Reset count if more than a minute has passed
            if now - last_request_time > timedelta(minutes=1):
                count = 0
        else:
            count = 0

        # Check if rate limit exceeded
        if count >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )

        # Update request count
        self.requests[client_ip] = (now, count + 1)

# Create a singleton instance
rate_limiter = RateLimiter()

# Create a dependency function
async def check_rate_limit(request: Request):
    await rate_limiter(request)
    return None

__all__ = ['check_rate_limit'] 