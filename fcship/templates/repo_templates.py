"""Repository templates"""


def get_repo_templates(name: str) -> dict[str, str]:
    """Get templates for repository files."""
    return {
        f"infrastructure/repositories/{name}_repository.py": f"""from typing import Optional, List
from sqlalchemy.orm import Session
from domain.{name}.entity import {name.title()}Entity
from domain.{name}.repository import {name.title()}Repository
from infrastructure.models.{name} import {name.title()}Model

class SQL{name.title()}Repository({name.title()}Repository):
    def __init__(self, session: Session):
        self.session = session
        
    def get(self, id: int) -> Optional[{name.title()}Entity]:
        model = self.session.query({name.title()}Model).filter({name.title()}Model.id == id).first()
        return model.to_entity() if model else None
        
    def list(self) -> List[{name.title()}Entity]:
        models = self.session.query({name.title()}Model).all()
        return [model.to_entity() for model in models]""",
        f"tests/infrastructure/repositories/test_{name}_repository.py": f"""import pytest
from infrastructure.repositories.{name}_repository import SQL{name.title()}Repository

def test_{name}_repository_get(db_session):
    # Arrange
    repo = SQL{name.title()}Repository(db_session)
    
    # Act & Assert
    result = repo.get(1)
    assert result is None  # Test with no data
    
def test_{name}_repository_list(db_session):
    # Arrange
    repo = SQL{name.title()}Repository(db_session)
    
    # Act
    result = repo.list()
    
    # Assert
    assert isinstance(result, list)""",
    }
