"""Test cases for type handling utilities."""
import pytest
from dataclasses import dataclass
from expression import Result, Ok, Error
from fcship.utils.type_utils import ensure_type, map_type

@dataclass
class TestType:
    value: str

def test_ensure_type_with_valid_input():
    """Test ensure_type with valid input."""
    result = ensure_type("test", TestType, "TestType")
    assert isinstance(result, TestType)
    assert result.value == "test"

def test_ensure_type_with_validation():
    """Test ensure_type with custom validation."""
    def validate(value):
        return Ok(value) if len(value) > 3 else Error("Value too short")
    
    result = ensure_type("test", TestType, "TestType", validate)
    assert isinstance(result, TestType)
    assert result.value == "test"

def test_ensure_type_with_failed_validation():
    """Test ensure_type with failing validation."""
    def validate(value):
        return Ok(value) if len(value) > 5 else Error("Value too short")
    
    with pytest.raises(ValueError):
        ensure_type("test", TestType, "TestType", validate)

def test_map_type_with_success():
    """Test map_type with successful transformation."""
    def transform(s: str) -> Result[str, Exception]:
        return Ok(s.upper())
    
    mapper = map_type(transform, TestType)
    result = mapper(TestType("test"))
    assert result.is_ok()
    assert result.ok == TestType("TEST")

def test_map_type_with_failure():
    """Test map_type with failed transformation."""
    def transform(s: str) -> Result[str, Exception]:
        return Error(ValueError("test error"))
    
    mapper = map_type(transform, TestType)
    result = mapper(TestType("test"))
    assert result.is_error()
    assert isinstance(result.error, ValueError)
    assert str(result.error) == "test error"