"""Test cases for validation utilities."""
import pytest
from expression import Result, Ok, Error
from fcship.utils.validation import (
    validate_operation,
    validate,
    compose_validations,
    sequence_validations
)

def test_validate_operation_with_valid_input():
    """Test validate_operation with valid operation."""
    result = validate_operation("create", ["create", "update", "delete"])
    assert result.is_ok()
    assert result.ok == "create"

def test_validate_operation_with_invalid_input():
    """Test validate_operation with invalid operation."""
    result = validate_operation("invalid", ["create", "update", "delete"])
    assert result.is_error()
    assert "Invalid operation" in str(result.error)

def test_validate_operation_with_required_name():
    """Test validate_operation when name is required."""
    result = validate_operation(
        "create",
        ["create", "update", "delete"],
        name="test",
        requires_name=["create"]
    )
    assert result.is_ok()
    assert result.ok == "create"

def test_validate_operation_missing_required_name():
    """Test validate_operation when required name is missing."""
    result = validate_operation(
        "create",
        ["create", "update", "delete"],
        name=None,
        requires_name=["create"]
    )
    assert result.is_error()
    assert "requires a name parameter" in str(result.error)

def test_validate_function():
    """Test validate function creation."""
    is_positive = validate(lambda x: x > 0, "Value must be positive")
    result = is_positive(5)
    assert result.is_ok()
    assert result.ok == 5

def test_validate_function_failure():
    """Test validate function with failing validation."""
    is_positive = validate(lambda x: x > 0, "Value must be positive")
    result = is_positive(-5)
    assert result.is_error()
    assert isinstance(result.error, Exception)
    assert str(result.error) == "Value must be positive"

def test_compose_validations():
    """Test composition of multiple validations."""
    is_positive = validate(lambda x: x > 0, "Value must be positive")
    is_less_than_ten = validate(lambda x: x < 10, "Value must be less than 10")
    
    composed = compose_validations(is_positive, is_less_than_ten)
    result = composed(5)
    assert result.is_ok()
    assert result.ok == 5

def test_compose_validations_failure():
    """Test composition with failing validation."""
    is_positive = validate(lambda x: x > 0, "Value must be positive")
    is_less_than_ten = validate(lambda x: x < 10, "Value must be less than 10")
    
    composed = compose_validations(is_positive, is_less_than_ten)
    result = composed(-5)
    assert result.is_error()
    assert isinstance(result.error, Exception)
    assert "Value must be positive" in str(result.error)

def test_sequence_validations():
    """Test sequencing multiple validation results."""
    results = [Ok(1), Ok(2), Ok(3)]
    result = sequence_validations(results)
    assert result.is_ok()
    assert result.ok == [1, 2, 3]

def test_sequence_validations_with_error():
    """Test sequencing with error result."""
    error = ValueError("test error")
    results = [Ok(1), Error(error), Ok(3)]
    result = sequence_validations(results)
    assert result.is_error()
    assert result.error == error