"""Playwright manager module using Expression for functional approach."""

import logging
import subprocess
import sys

from collections.abc import Generator

from expression import effect
from expression.core import Error, Ok, Result


def check_playwright() -> Result[bool, Exception]:
    """Check if Playwright is installed."""
    try:
        import importlib.util

        if importlib.util.find_spec("playwright") is not None:
            return Ok(True)
        return Ok(False)
    except ImportError:
        return Ok(False)


def install_playwright_package() -> Result[bool, Exception]:
    """Install Playwright package."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
        return Ok(True)
    except subprocess.CalledProcessError as e:
        return Error(e)


def install_playwright_browser() -> Result[bool, Exception]:
    """Install Playwright browser."""
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        return Ok(True)
    except subprocess.CalledProcessError as e:
        return Error(e)


@effect.result[bool, Exception]()
def ensure_playwright() -> Generator[Result[bool, Exception], None, bool]:
    """Ensure Playwright is installed and ready to use using ROP."""
    is_installed = yield from check_playwright()

    if is_installed:
        return True

    # Install process using railway oriented programming
    yield from install_playwright_package()
    yield from install_playwright_browser()
    return True


def get_playwright():
    """Get Playwright module with lazy import using ROP."""
    result = ensure_playwright()

    match result:
        case Ok(_):
            try:
                from playwright.async_api import async_playwright

                return async_playwright
            except ImportError as e:
                logging.exception(f"Failed to import playwright: {e!s}")
                return None
        case Error(e):
            logging.error(f"Failed to setup Playwright: {e!s}")
            print("\nError: Failed to setup Playwright.")
            print("Please try installing it manually with these commands:")
            print("  pip install playwright")
            print("  playwright install")
            return None
