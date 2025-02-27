"""Rate limiter with functional approach."""

import asyncio
import time

from dataclasses import dataclass
from typing import Any

from expression import Error, Ok, Result

from .exceptions import ProcessingException, capture_exception
from .logger import FunctionalLogger
from .types import Url


@dataclass
class RateLimit:
    """Rate limit configuration."""

    requests_per_second: float
    burst_size: int


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, rate_limit: RateLimit):
        self.rate = rate_limit.requests_per_second
        self.burst_size = rate_limit.burst_size
        self.tokens = rate_limit.burst_size
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()
        self._domain_limiters: dict[str, RateLimiter] = {}

    async def add_tokens(self) -> None:
        """Add tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_update
        new_tokens = elapsed * self.rate
        self.tokens = min(self.burst_size, self.tokens + new_tokens)
        self.last_update = now

    async def acquire(self, logger: FunctionalLogger) -> Result[None, ProcessingException]:
        """Acquire a token with ROP."""
        try:
            async with self.lock:
                await self.add_tokens()
                if self.tokens < 1:
                    wait_time = (1 - self.tokens) / self.rate
                    await logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    await self.add_tokens()

                self.tokens -= 1
                return Ok(None)
        except Exception as e:
            return capture_exception(e, ProcessingException, "Failed to acquire rate limit token")

    def get_domain_limiter(self, domain: str) -> "RateLimiter":
        """Get or create a rate limiter for a specific domain."""
        if domain not in self._domain_limiters:
            # More conservative rate limit for individual domains
            self._domain_limiters[domain] = RateLimiter(
                RateLimit(
                    requests_per_second=self.rate / 2, burst_size=max(1, self.burst_size // 2)
                )
            )
        return self._domain_limiters[domain]


async def with_rate_limit(
    url: Url,
    rate_limiter: RateLimiter,
    logger: FunctionalLogger,
    operation: callable,
    *args,
    **kwargs,
) -> Result[Any, ProcessingException]:
    """Execute operation with rate limiting using ROP."""
    try:
        # Get domain-specific limiter
        from urllib.parse import urlparse

        domain = urlparse(url).netloc
        domain_limiter = rate_limiter.get_domain_limiter(domain)

        # Acquire tokens from both global and domain limiters
        global_result = await rate_limiter.acquire(logger)
        if isinstance(global_result, Error):
            return global_result

        domain_result = await domain_limiter.acquire(logger)
        if domain_result.is_error():
            return domain_result

        # Execute the operation
        return await operation(*args, **kwargs)

    except Exception as e:
        return capture_exception(e, ProcessingException, f"Rate limited operation failed for {url}")
