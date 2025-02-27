# CLI Tool and VSCode Snippets Plan

## CLI Tool Design

### Command Structure
```bash
craftsmanship [command] [options]
```

### Core Commands

#### 1. Domain Generation
```bash
craftsmanship domain create [domain-name]
```
Creates a new domain with all required files:
- domain/[name]/entity.py
- domain/[name]/repository.py
- domain/[name]/exceptions.py
- domain/[name]/value_objects.py
- domain/[name]/schemas.py

#### 2. Service Generation
```bash
craftsmanship service create [service-name]
```
Creates a new service with required files:
- service/[name]/service.py
- service/[name]/dto.py
- service/[name]/mapper.py

#### 3. API Route Generation
```bash
craftsmanship api create [route-name]
```
Creates new API endpoint files:
- api/v1/[name].py
- api/schemas/[name].py
- tests/api/test_[name].py

#### 4. Repository Generation
```bash
craftsmanship repo create [repo-name]
```
Creates repository implementation:
- infrastructure/repositories/[name]_repository.py
- tests/infrastructure/repositories/test_[name]_repository.py

#### 5. Test Generation
```bash
craftsmanship test create [type] [name]
```
Creates test files based on type:
- Unit test: tests/unit/[path]/test_[name].py
- Integration test: tests/integration/[path]/test_[name].py

### Helper Commands

#### 1. Project Scaffolding
```bash
craftsmanship project init [project-name]
```
Initializes new project with basic structure

#### 2. Migration Management
```bash
craftsmanship db migration create [name]
craftsmanship db migrate
craftsmanship db rollback
```

#### 3. Code Verification
```bash
craftsmanship verify
```
Runs:
- Type checking
- Linting
- Tests
- Format checking

## VSCode Snippets

### 1. Domain Layer Snippets

#### Domain Entity
```json
{
  "Domain Entity": {
    "prefix": "entity",
    "body": [
      "from dataclasses import dataclass",
      "from domain.base import Entity",
      "",
      "@dataclass",
      "class ${1:Name}Entity(Entity):",
      "    id: int",
      "    ${2:attribute}: ${3:type}",
      "",
      "    def validate(self) -> None:",
      "        ${4:pass}",
      ""
    ]
  }
}
```

#### Repository Interface
```json
{
  "Repository Interface": {
    "prefix": "repo-interface",
    "body": [
      "from typing import Protocol, Optional",
      "from domain.${1:name}.entity import ${2:Name}Entity",
      "",
      "class ${2:Name}Repository(Protocol):",
      "    def get(self, id: int) -> Optional[${2:Name}Entity]:",
      "        ...",
      "",
      "    def create(self, entity: ${2:Name}Entity) -> ${2:Name}Entity:",
      "        ...",
      "",
      "    def update(self, entity: ${2:Name}Entity) -> ${2:Name}Entity:",
      "        ...",
      "",
      "    def delete(self, id: int) -> None:",
      "        ...",
      ""
    ]
  }
}
```

### 2. Service Layer Snippets

#### Service Class
```json
{
  "Service Class": {
    "prefix": "service",
    "body": [
      "from domain.${1:name}.repository import ${2:Name}Repository",
      "from service.${1:name}.dto import ${2:Name}DTO",
      "",
      "class ${2:Name}Service:",
      "    def __init__(self, repository: ${2:Name}Repository):",
      "        self.repository = repository",
      "",
      "    async def get(self, id: int) -> ${2:Name}DTO:",
      "        entity = await self.repository.get(id)",
      "        return ${2:Name}DTO.from_entity(entity)",
      ""
    ]
  }
}
```

#### DTO Class
```json
{
  "DTO Class": {
    "prefix": "dto",
    "body": [
      "from dataclasses import dataclass",
      "from domain.${1:name}.entity import ${2:Name}Entity",
      "",
      "@dataclass",
      "class ${2:Name}DTO:",
      "    ${3:attribute}: ${4:type}",
      "",
      "    @classmethod",
      "    def from_entity(cls, entity: ${2:Name}Entity) -> '${2:Name}DTO':",
      "        return cls(",
      "            ${3:attribute}=entity.${3:attribute},",
      "        )",
      ""
    ]
  }
}
```

### 3. Infrastructure Layer Snippets

#### Repository Implementation
```json
{
  "Repository Implementation": {
    "prefix": "repo-impl",
    "body": [
      "from typing import Optional",
      "from sqlalchemy.orm import Session",
      "from domain.${1:name}.entity import ${2:Name}Entity",
      "from domain.${1:name}.repository import ${2:Name}Repository",
      "",
      "class SQL${2:Name}Repository(${2:Name}Repository):",
      "    def __init__(self, session: Session):",
      "        self.session = session",
      "",
      "    def get(self, id: int) -> Optional[${2:Name}Entity]:",
      "        ${0}",
      ""
    ]
  }
}
```

### 4. API Layer Snippets

#### Router
```json
{
  "FastAPI Router": {
    "prefix": "router",
    "body": [
      "from fastapi import APIRouter, Depends, HTTPException",
      "from app.api.deps import get_current_user",
      "from service.${1:name}.service import ${2:Name}Service",
      "from app.api.schemas.${1:name} import ${2:Name}Create, ${2:Name}Response",
      "",
      "router = APIRouter(prefix='/${1:name}s', tags=['${2:Name}s'])",
      "",
      "@router.post('/', response_model=${2:Name}Response)",
      "async def create_${1:name}(",
      "    data: ${2:Name}Create,",
      "    service: ${2:Name}Service = Depends(),",
      "    current_user = Depends(get_current_user)",
      "):",
      "    return await service.create(data, current_user)",
      ""
    ]
  }
}
```

#### Schema
```json
{
  "Pydantic Schema": {
    "prefix": "schema",
    "body": [
      "from pydantic import BaseModel",
      "",
      "class ${1:Name}Base(BaseModel):",
      "    ${2:attribute}: ${3:type}",
      "",
      "class ${1:Name}Create(${1:Name}Base):",
      "    pass",
      "",
      "class ${1:Name}Response(${1:Name}Base):",
      "    id: int",
      "",
      "    class Config:",
      "        orm_mode = True",
      ""
    ]
  }
}
```

### 5. Test Snippets

#### Unit Test
```json
{
  "Unit Test": {
    "prefix": "test-unit",
    "body": [
      "import pytest",
      "from unittest.mock import Mock",
      "",
      "def test_${1:function_name}():",
      "    # Arrange",
      "    ${2:arrange}",
      "",
      "    # Act",
      "    ${3:act}",
      "",
      "    # Assert",
      "    ${4:assert}",
      ""
    ]
  }
}
```

#### Integration Test
```json
{
  "Integration Test": {
    "prefix": "test-integration",
    "body": [
      "import pytest",
      "from httpx import AsyncClient",
      "",
      "async def test_${1:endpoint_name}(",
      "    client: AsyncClient,",
      "    ${2:fixtures}",
      "):",
      "    # Arrange",
      "    ${3:arrange}",
      "",
      "    # Act",
      "    response = await client.${4:method}('${5:endpoint}')",
      "",
      "    # Assert",
      "    assert response.status_code == ${6:200}",
      "    ${7:additional_assertions}",
      ""
    ]
  }
}
```

## Installation and Setup

1. Install CLI tool:
```bash
pip install craftsmanship
```

2. Install VSCode snippets:
- Copy snippets to `.vscode/craftsmanship.code-snippets`
- Or use VSCode extension marketplace

## Usage Guidelines

1. Always use CLI for generating new components:
```bash
# Creating a new domain
craftsmanship domain create user

# Creating a service
craftsmanship service create user

# Creating API endpoints
craftsmanship api create user
```

2. Use snippets for implementation:
- `entity` - Create domain entities
- `repo-interface` - Create repository interfaces
- `service` - Create service classes
- `dto` - Create DTOs
- `router` - Create API routes
- `schema` - Create Pydantic schemas
- `test-unit` - Create unit tests
- `test-integration` - Create integration tests

3. Follow the verification process:
```bash
# Before committing
craftsmanship verify