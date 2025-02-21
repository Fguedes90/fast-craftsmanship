"""Test cases for functional programming utilities."""
import pytest
from expression import Result, Ok, Error, Option, Some, Nothing
from fcship.utils.functional import (
    catch_errors,
    sequence_results,
    tap,
    tap_async,
    lift_option
)

def test_catch_errors_with_success():
    """Test catch_errors decorator with successful execution."""
    @catch_errors
    def success_fn():
        return Ok("success")
    
    result = success_fn()
    assert isinstance(result, Result)
    assert result.is_ok()
    assert result.ok == "success"

def test_catch_errors_with_exception():
    """Test catch_errors decorator with exception."""
    @catch_errors
    def failing_fn():
        raise ValueError("test error")
    
    result = failing_fn()
    assert isinstance(result, Result)
    assert result.is_error()
    assert isinstance(result.error, ValueError)
    assert str(result.error) == "test error"

def test_sequence_results_with_all_success():
    """Test sequence_results with all successful results."""
    results = [Ok("1"), Ok("2"), Ok("3")]
    combined = sequence_results(results)
    assert combined.is_ok()
    assert combined.ok == ["1", "2", "3"]

def test_sequence_results_with_failure():
    """Test sequence_results with a failure."""
    results = [Ok("1"), Error(ValueError("test")), Ok("3")]
    combined = sequence_results(results)
    assert combined.is_error()
    assert isinstance(combined.error, ValueError)

def test_tap_with_side_effect():
    """Test tap with side effect."""
    side_effect_value = []
    def side_effect(x):
        side_effect_value.append(x)
    
    result = Ok(42).map(tap(side_effect))
    assert result.is_ok()
    assert result.ok == 42
    assert side_effect_value == [42]

@pytest.mark.asyncio
async def test_tap_async_with_side_effect():
    """Test tap_async with async side effect."""
    side_effect_value = []
    async def async_side_effect(x):
        side_effect_value.append(x)
    
    result = await tap_async(async_side_effect)(42)
    assert result == 42
    assert side_effect_value == [42]

def test_lift_option_with_some():
    """Test lift_option with Some value."""
    def get_optional(x: int) -> Option[int]:
        return Some(x) if x > 0 else Nothing
    
    lifted = lift_option(get_optional)
    result = lifted(42)
    assert result.is_ok()
    assert result.ok == 42

def test_lift_option_with_nothing():
    """Test lift_option with Nothing."""
    def get_optional(x: int) -> Option[int]:
        return Some(x) if x > 0 else Nothing
    
    lifted = lift_option(get_optional)
    result = lifted(-1)
    assert result.is_error()
    assert isinstance(result.error, Exception)