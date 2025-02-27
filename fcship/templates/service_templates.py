"""Service templates"""


def get_service_templates(name: str) -> dict[str, str]:
    """Get templates for service files."""
    return {
        "service.py": f"""from domain.{name}.repository import {name.title()}Repository
from .dto import {name.title()}DTO

class {name.title()}Service:
    def __init__(self, repository: {name.title()}Repository):
        self.repository = repository""",
        "dto.py": f"""from dataclasses import dataclass
from domain.{name}.entity import {name.title()}Entity

@dataclass
class {name.title()}DTO:
    @classmethod
    def from_entity(cls, entity: {name.title()}Entity) -> '{name.title()}DTO':
        return cls()""",
        "mapper.py": f"""from domain.{name}.entity import {name.title()}Entity
from .dto import {name.title()}DTO

def to_dto(entity: {name.title()}Entity) -> {name.title()}DTO:
    return {name.title()}DTO.from_entity(entity)""",
    }
