"""Domain templates"""


def get_domain_templates(name: str) -> dict[str, str]:
    """Get templates for domain files."""
    return {
        "entity.py": f"""from dataclasses import dataclass
from domain.base import Entity

@dataclass
class {name.title()}Entity(Entity):
    pass""",
        "repository.py": f"""from typing import Protocol, Optional
from .entity import {name.title()}Entity

class {name.title()}Repository(Protocol):
    pass""",
        "exceptions.py": f"""class {name.title()}Error(Exception):
    pass""",
        "value_objects.py": f"# Value objects for {name} domain",
        "schemas.py": f"""from pydantic import BaseModel

class {name.title()}Schema(BaseModel):
    pass""",
    }
