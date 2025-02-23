import pytest
from expression import Ok, Error, Result, effect
from rich.progress import Progress, SpinnerColumn, TextColumn
from fcship.tui.progress import (
    ProgressConfig,
    create_progress_config,
    create_progress,
    display_progress,
    safe_display_with_progress,
    run_with_timeout,
)
from fcship.tui.errors import DisplayError
import asyncio

@pytest.fixture
def sample_config():
    return create_progress_config("Test Progress", 10)

def test_create_progress_config():
    """Test progress configuration creation"""
    config = create_progress_config("Test", 5)
    assert isinstance(config, ProgressConfig)
    assert config.description == "Test"
    assert config.total == 5
    assert len(config.columns) > 0
    assert isinstance(config.columns[0], SpinnerColumn)
    assert isinstance(config.columns[1], TextColumn)

def test_create_progress_success(sample_config):
    """Test successful progress bar creation"""
    result = create_progress(sample_config)
    assert result.is_ok()
    assert isinstance(result.ok, Progress)

def test_create_progress_error():
    """Test progress bar creation with invalid config"""
    config = ProgressConfig(description="Test", total=-1, columns=[])
    result = create_progress(config)
    assert result.is_error()
    assert result.error.tag == "rendering"

@effect.result[None, DisplayError]()
async def test_display_progress_validation():
    """Test input validation for display_progress"""
    # Test with empty items list
    result = await display_progress([], lambda x: Ok(x), "Test")
    assert result.is_error()
    assert result.error.tag == "validation"

    # Test with None process function
    result = await display_progress([1, 2, 3], None, "Test")
    assert result.is_error()
    assert result.error.tag == "validation"

    # Test with empty description
    result = await display_progress([1, 2, 3], lambda x: Ok(x), "")
    assert result.is_error()
    assert result.error.tag == "validation"

@effect.result[None, DisplayError]()
async def test_display_progress_success():
    """Test successful progress display"""
    items = [1, 2, 3]
    async def process(x):
        await asyncio.sleep(0.1)
        return Ok(x * 2)

    result = await display_progress(items, process, "Processing items")
    assert result.is_ok()

@effect.result[None, DisplayError]()
async def test_safe_display_with_progress(sample_config):
    """Test safe progress display with error handling"""
    progress = create_progress(sample_config).ok
    items = [1, 2, 3]
    
    # Test successful processing
    async def success_process(x):
        await asyncio.sleep(0.1)
        return Ok(x)

    result = await safe_display_with_progress(
        progress, items, success_process, "Success test"
    )
    assert result.is_ok()

    # Test with failing process
    async def fail_process(x):
        await asyncio.sleep(0.1)
        return Error(DisplayError.Execution("Failed", "test error"))

    result = await safe_display_with_progress(
        progress, items, fail_process, "Failure test"
    )
    assert result.is_error()
    assert result.error.tag == "execution"

@effect.result[int, DisplayError]()
async def test_run_with_timeout():
    """Test timeout functionality"""
    # Test successful completion within timeout
    async def quick_task():
        await asyncio.sleep(0.1)
        return Ok(42)

    result = await run_with_timeout(quick_task(), 1.0)
    assert result.is_ok()
    assert result.ok == 42

    # Test timeout
    async def slow_task():
        await asyncio.sleep(2.0)
        return Ok(42)

    result = await run_with_timeout(slow_task(), 0.1)
    assert result.is_error()
    assert result.error.tag == "timeout"

@effect.result[None, DisplayError]()
async def test_display_progress_error_handling():
    """Test error handling in progress display"""
    items = [1, 2, 3]
    async def error_process(x):
        await asyncio.sleep(0.1)
        if x == 2:
            return Error(DisplayError.Execution("Failed", "test error"))
        return Ok(x)

    result = await display_progress(items, error_process, "Error test")
    assert result.is_error()
    assert result.error.tag == "execution" 