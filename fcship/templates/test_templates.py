"""Test templates"""


def get_test_template(test_type: str, name: str) -> str:
    """Get template for test file based on type."""
    if test_type == "unit":
        return f"""import pytest
from unittest.mock import Mock

def test_{name}_creation():
    # Arrange
    mock_repo = Mock()
    
    # Act
    result = None  # TODO: Implement test
    
    # Assert
    assert True  # TODO: Add real assertions"""
    # integration
    return f"""import pytest
from httpx import AsyncClient

async def test_{name}_integration(
    client: AsyncClient,
    db_session,
):
    # Arrange
    # TODO: Setup test data
    
    # Act
    response = await client.get('/{name}s/')
    
    # Assert
    assert response.status_code == 200"""
