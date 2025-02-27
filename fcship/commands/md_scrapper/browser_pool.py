"""Browser pool manager with functional approach."""

from collections.abc import AsyncGenerator
from dataclasses import dataclass

from expression import Error, Ok, Result
from playwright.async_api import Browser, BrowserContext, async_playwright

from .exceptions import ProcessingException, capture_exception
from .logger import FunctionalLogger


@dataclass
class BrowserPool:
    """Manages a pool of browser instances."""

    browsers: list[Browser]
    contexts: list[BrowserContext]
    current_index: int = 0

    @classmethod
    async def create(
        cls, instances: int, logger: FunctionalLogger
    ) -> Result["BrowserPool", ProcessingException]:
        """Create a new browser pool."""
        try:
            await logger.info(f"Creating browser pool with {instances} instances")
            p = await async_playwright().start()

            browsers: list[Browser] = []
            contexts: list[BrowserContext] = []

            for i in range(instances):
                await logger.debug(f"Launching browser instance {i + 1}")
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()

                browsers.append(browser)
                contexts.append(context)

            return Ok(cls(browsers=browsers, contexts=contexts))
        except Exception as e:
            return capture_exception(e, ProcessingException, "Failed to create browser pool")

    def get_next_context(self) -> BrowserContext:
        """Get next available browser context using round-robin."""
        context = self.contexts[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.contexts)
        return context

    async def cleanup(self, logger: FunctionalLogger) -> Result[None, ProcessingException]:
        """Clean up all browser resources."""
        try:
            await logger.info("Cleaning up browser pool")
            for i, (browser, context) in enumerate(zip(self.browsers, self.contexts, strict=False)):
                await logger.debug(f"Closing browser instance {i + 1}")
                await context.close()
                await browser.close()
            return Ok(None)
        except Exception as e:
            return capture_exception(e, ProcessingException, "Failed to cleanup browser pool")


async def with_browser_pool(
    instances: int, logger: FunctionalLogger
) -> AsyncGenerator[Result[BrowserPool, ProcessingException], None]:
    """Context manager for browser pool."""
    pool_result = await BrowserPool.create(instances, logger)

    if isinstance(pool_result, Error):
        yield pool_result
        return

    try:
        yield pool_result
    finally:
        await pool_result.value.cleanup(logger)
