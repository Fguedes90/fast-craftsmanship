"""API templates"""


def get_api_templates(name: str) -> dict[str, str]:
    """Get templates for API files."""
    return {
        f"api/v1/{name}.py": f"""from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user
from service.{name}.service import {name.title()}Service
from app.api.schemas.{name} import {name.title()}Response

router = APIRouter(prefix='/{name}s', tags=['{name.title()}s'])

@router.get('/', response_model=list[{name.title()}Response])
async def list_{name}s(
    service: {name.title()}Service = Depends(),
    current_user = Depends(get_current_user)
):
    return await service.list()""",
        f"api/schemas/{name}.py": f"""from pydantic import BaseModel

class {name.title()}Base(BaseModel):
    name: str

class {name.title()}Create({name.title()}Base):
    pass

class {name.title()}Response({name.title()}Base):
    id: int

    class Config:
        orm_mode = True""",
        f"tests/api/test_{name}.py": f"""import pytest
from httpx import AsyncClient

async def test_{name}_endpoints(
    client: AsyncClient,
    db_session
):
    # Arrange
    # TODO: Setup test data
    
    # Act
    response = await client.get('/{name}s/')
    
    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), list)""",
    }
