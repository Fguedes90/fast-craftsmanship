
from collections.abc import Generator
from typing import Any

import pytest

from expression import Error, Ok, Result, effect, pipe
from rich.progress import Progress, SpinnerColumn, TextColumn

from fcship.tui.progress import (
    ProgressConfig,
    ProgressError,
    create_context,
    create_progress,
    create_progress_config,
    display_progress,
    run_with_timeout,
    safe_display_with_progress,
)


@pytest.fixture
def sample_config() -> Result[ProgressConfig, ProgressError]:
    return create_progress_config("Test Progress", 10)


def test_create_progress_config():
    """Test progress configuration creation"""
    # Test successful creation
    result = create_progress_config("Test", 5)
    assert result.is_ok()
    config = result.ok
    assert isinstance(config, ProgressConfig)
    assert config.description == "Test"
    assert config.total == 5
    assert len(config.columns) > 0
    assert isinstance(config.columns[0], SpinnerColumn)
    assert isinstance(config.columns[1], TextColumn)
    assert config.parallel is False
    assert config.max_workers is None

    # Test parallel configuration
    result = create_progress_config("Test", 5, parallel=True, max_workers=2)
    assert result.is_ok()
    config = result.ok
    assert config.parallel is True
    assert config.max_workers == 2


def test_create_progress_success(sample_config):
    """Test successful progress bar creation"""
    result = pipe(sample_config, lambda r: r.bind(create_progress))
    assert result.is_ok()
    assert isinstance(result.ok, Progress)


def test_create_progress_error():
    """Test progress bar creation with invalid config"""
    result = create_progress_config("Test", -1)
    assert result.is_error()
    assert result.error.tag == "validation"


def test_display_progress_validation():
    """Test input validation for display_progress"""

    @effect.result[None, ProgressError]()
    def run_test():
        def mock_process(x: Any) -> Generator[Any, Any, Result[Any, Any]]:
            yield from []
            return Ok(x)

        # Test with empty items list
        result = yield from display_progress([], mock_process, "Test")
        assert result.is_error()
        assert isinstance(result.error, ProgressError)
        assert result.error.tag == "validation"

        # Test with None process function
        result = yield from display_progress([1, 2, 3], None, "Test")  # type: ignore
        assert result.is_error()
        assert isinstance(result.error, ProgressError)
        assert result.error.tag == "validation"

        # Test with empty description
        result = yield from display_progress([1, 2, 3], mock_process, "")
        assert result.is_error()
        assert isinstance(result.error, ProgressError)
        assert result.error.tag == "validation"

    run_test()


def test_display_progress_sequential():
    """Test sequential progress display"""

    @effect.result[None, ProgressError]()
    def run_test():
        items = [1, 2, 3]

        def process(x: int) -> Generator[Any, Any, Result[int, str]]:
            yield from []
            return Ok(x * 2)

        result = yield from display_progress(items, process, "Processing items")
        assert result.is_ok()

    run_test()


def test_display_progress_parallel():
    """Test parallel progress display"""

    @effect.result[None, ProgressError]()
    def run_test():
        items = [1, 2, 3]

        def process(x: int) -> Generator[Any, Any, Result[int, str]]:
            yield from []
            return Ok(x * 2)

        result = yield from display_progress(
            items, process, "Processing items", parallel=True, max_workers=2
        )
        assert result.is_ok()

    run_test()


def test_safe_display_with_progress(sample_config):
    """Test safe progress display with error handling"""

    @effect.result[None, ProgressError]()
    def run_test():
        items = [1, 2, 3]

        # Test successful processing
        def success_process(x: int) -> Generator[Any, Any, Result[int, str]]:
            yield from []
            return Ok(x)

        # Successful case
        config = sample_config.ok
        progress = yield from create_progress(config)
        context = yield from create_context(progress, items, success_process, "Success test")
        result = yield from safe_display_with_progress(context)
        assert result.is_ok()

        # Test with failing process
        def fail_process(x: int) -> Generator[Any, Any, Result[int, str]]:
            yield from []
            return Error("test error")

        # Failing case
        progress = yield from create_progress(config)
        context = yield from create_context(progress, items, fail_process, "Failure test")
        result = yield from safe_display_with_progress(context)
        assert result.is_error()
        assert result.error.tag == "parallel"

    run_test()


def test_run_with_timeout():
    """Test timeout functionality"""

    @effect.result[int, ProgressError]()
    def run_test():
        # Test successful completion
        def quick_task() -> Generator[Any, Any, Result[int, str]]:
            yield from []
            return Ok(42)

        result = yield from run_with_timeout(quick_task(), 1.0)
        assert result.is_ok()
        assert result.ok == 42

        # Test error
        def error_task() -> Generator[Any, Any, Result[int, str]]:
            yield from []
            return Error("test error")

        result = yield from run_with_timeout(error_task(), 1.0)
        assert result.is_error()
        assert result.error.tag == "execution"

    run_test()


def test_display_progress_error_handling():
    """Test error handling in progress display"""

    @effect.result[None, ProgressError]()
    def run_test():
        items = [1, 2, 3]

        def error_process(x: int) -> Generator[Any, Any, Result[int, str]]:
            yield from []
            if x == 2:
                return Error("test error")
            return Ok(x)

        # Test sequential error handling
        result = yield from display_progress(items, error_process, "Error test")
        assert result.is_error()
        assert result.error.tag == "parallel"

        # Test parallel error handling
        result = yield from display_progress(
            items, error_process, "Error test", parallel=True, max_workers=2
        )
        assert result.is_error()
        assert result.error.tag == "parallel"

    run_test()


def test_progress_error_creation():
    """Test ProgressError creation methods"""
    # Test from_error
    error = ProgressError.from_error("test error")
    assert error.tag == "execution"
    assert error.execution[0] == "Operation failed"
    assert error.execution[1] == "test error"

    # Test from_parallel_errors
    error = ProgressError.from_parallel_errors(["error1", "error2"])
    assert error.tag == "parallel"
    assert error.parallel[0] == "Some parallel tasks failed"
    assert error.parallel[1] == ["error1", "error2"]
